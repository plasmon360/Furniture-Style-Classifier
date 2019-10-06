from .imports import * 
class Callback():
    "Taken from Fastai. Base class for callbacks that want to record values, dynamically change learner params, etc."
    
    def on_train_begin(self, **kwargs):
        "To initialize constants in the callback."
        pass

    def on_epoch_begin(self, **kwargs):
        "At the beginning of each epoch."
        pass
    
    def on_phase_begin(self, **kwargs):
        "Set train/test here"
        pass
        
    def on_batch_begin(self, **kwargs):
        "Set HP before the output and loss are computed."
        pass
    
    def on_loss_begin(self, **kwargs):
        "Called after forward pass but before loss has been computed."
        pass
    
    def on_backward_begin(self, **kwargs):
        "Called after the forward pass and the loss has been computed, but before backprop."
        pass
    
    def on_backward_end(self, **kwargs):
        "Called after backprop but before optimizer step. Useful for true weight decay in AdamW."
        pass
    
    
    def on_step_end(self, **kwargs):
        "Called after the step of the optimizer but before the gradients are zeroed."
        pass
    
    def on_batch_end(self, **kwargs):
        "Called at the end of the batch."
        pass
    
    def on_phase_end(self, **kwargs):
        "Called at the end of train/test phase"
        pass
    
    def on_epoch_end(self, **kwargs):
        "Called at the end of an epoch."
        pass
    
    def on_train_end(self, **kwargs):
        "Useful for cleaning up things and saving files/models."
        pass


class MyLrFinder(Callback):
    
    def __init__(self, learner, start_lr=1E-4, stop_lr=5, num_iterations=100):
        super().__init__()
        self.learner = learner
        self.opt = learner.optimizer
        self.num_iterations = num_iterations
        self.lr_increment = (stop_lr/start_lr)**(1/self.num_iterations)
        self.start_lr = start_lr
        self.stop_lr = stop_lr
        
    def on_train_begin(self):
        self.lr_rates = []
        self.b_losses = {'train': [], 'val': []}
        for param_group in self.opt.param_groups:
            param_group['lr'] = self.start_lr
        
    def on_batch_begin(self):
        if self.learner.phase == 'train':
            for param_group in self.opt.param_groups:
    #             print(f"lr : {param_group['lr']}")
                self.lr_rates.append(param_group['lr'])

    def on_batch_end(self):
        if self.learner.phase == 'train':
            for param_group in self.opt.param_groups:
                param_group['lr'] = param_group['lr'] * self.lr_increment
            self.b_losses[self.learner.phase].append(self.learner.batch_loss.detach().cpu().numpy())
        
    def plot_loss_vs_batch(self):
        plt.semilogx(self.lr_rates, self.b_losses['train'], label='Train')
        plt.xlabel('Learning rate')
        plt.ylabel('Loss')
        plt.legend()
        plt.show()
    
    def plot_lr_with_iteration(self):
        plt.semilogy(self.lr_rates)
        plt.ylabel('Learning Rates')
        plt.xlabel('Iteration')
        plt.show()
        
class Cyclic_LR(Callback):
    
    def __init__(self, learner, min_lr=1E-4, max_lr=5, stepsize=100, policy='triangular'):
        super().__init__()
        self.learner = learner
        self.opt = learner.optimizer
        self.stepsize = stepsize
        self.min_lr = min_lr
        self.max_lr = max_lr  
        self.policy = policy
        
    def on_train_begin(self):
        self.lr_rates = []
        self.b_losses = {'train': [], 'val': []}
        self.iteration = 0
        for param_group in self.opt.param_groups:
            param_group['lr'] = self.min_lr
  
    def on_batch_begin(self):
        if self.learner.phase == 'train':
            cycle = math.floor(self.iteration/(2*self.stepsize))
            x = abs((self.iteration - (2*cycle + 1)*self.stepsize)/self.stepsize)
            for param_group in self.opt.param_groups:
                if self.policy == 'triangular':
                    param_group['lr'] = self.min_lr + (self.max_lr-self.min_lr)*max([0, 1-x])
                elif self.policy == 'triangular2':
                    param_group['lr'] = self.min_lr + (self.max_lr-self.min_lr)*min([1, max([0, 1-x])/2**cycle])
     #             print(f"lr : {param_group['lr']}")
                self.lr_rates.append(param_group['lr'])
                  
    def on_batch_end(self):
        if self.learner.phase == 'train':
            self.iteration += 1
    
    def plot_lr_with_iteration(self):
        plt.plot(self.lr_rates)
        plt.ylabel('Learning Rates')
        plt.xlabel('Iteration')
        plt.show()
        
        
class RecordMetric(Callback):
    
    def __init__(self, learner, history=True):
        super().__init__()
        self.learner = learner
        self.opt = learner.optimizer
        self.train_dl = learner.data['dl']['train']
        self.history = history
                
    def accuracy(self):
        return (self.learner.preds == self.learner.targets).double().mean()*100
        
    def on_train_begin(self):
        #These variables keep track infomration averaged over certain epoch
        if (self.learner.checkpoint_source is not None) and self.learner.checkpoint_source.exists():
            checkpoint = torch.load(self.learner.checkpoint_source)
            print(f"Loading model from {self.learner.checkpoint_source}")
            self.learner.model.load_state_dict(checkpoint['model'])
            self.e_count = checkpoint['e_count']
            self.e_losses = checkpoint['e_losses']
            self.e_metric = checkpoint['metric']
        else:
            
            self.e_count = 0
            self.e_losses = {'train': [], 'val': []}
            self.e_metric = {'train': [], 'val': []}
        
        self.epoch_time = []
        
        # These variables keep track through all iterations over all epochs
        self.iteration = {'train': 0, 'val': 0} 
        self.i_losses = {'train': [], 'val': []}
        self.i_metric = {'train': [], 'val': []}
        
        self.best_metric = 0
        
    def on_epoch_begin(self):
        self.e_count += 1
        self.start_epoch = time.time()
        self.b_losses = {'train': [], 'val': []}
        self.b_metric = {'train': [], 'val': []}
        
    def on_batch_begin(self):
        self.iteration[self.learner.phase] += 1
    
    def on_batch_end(self):
        self.b_losses[self.learner.phase].append(self.learner.batch_loss.detach().cpu().numpy())
        self.b_metric[self.learner.phase].append(self.accuracy())

    def on_epoch_end(self):
        self.end_epoch = time.time()
        self.epoch_time.append(self.end_epoch - self.start_epoch)
        for phase in self.learner.phases:
            self.e_losses[phase].append(sum(self.b_losses[phase])/len(self.b_losses[phase]))
            self.e_metric[phase].append(sum(self.b_metric[phase])/len(self.b_metric[phase]))
            print(f"Epoch:{self.e_count} | {phase} Loss: {self.e_losses[phase][-1]:.2f} | Metric : {self.e_metric[phase][-1]:.3f}")
        
            self.i_losses[phase].extend(self.b_losses[phase])
            self.i_metric[phase].extend(self.b_metric[phase])
        
        if (self.e_metric['val'][-1].item() >= self.best_metric):
            checkpoint = {}
            checkpoint['e_count'] = self.e_count 
            checkpoint['e_losses'] = self.e_losses
            checkpoint['metric'] = self.e_metric 
            checkpoint['model'] = self.learner.model.state_dict()
            if not self.learner.checkpoint_source:
                checkpoint_dir = Path("../Checkpoints")
                if not checkpoint_dir.exists():
                    checkpoint_dir.mkdir(parents=True, exist_ok=True)
                filename = "checkpoint.pth"
                destination = checkpoint_dir/filename
            else:
                destination = self.learner.checkpoint_source

            print(f"Saving to {destination}")
            torch.save(checkpoint, destination)
            self.best_metric = self.e_metric['val'][-1].item()
        print("-"*25)

    def plot_losses_metric_with_iteration(self, i_space=1):
        fig, ax = plt.subplots(nrows=1, ncols=2)
        ax[0].set_title("Minibatch Loss with Iteration")
        ax[1].set_title("Metric with Iteration")
        for phase in self.learner.phases:
            ax[0].plot(range(1, self.iteration[phase]+1, i_space), self.i_losses[phase][::i_space], label=phase)
            ax[1].plot(range(1, self.iteration[phase]+1, i_space), self.i_metric[phase][::i_space], label=phase)
        ax[0].set_xlabel('Iteration')
        ax[1].set_xlabel('Iteration')
        ax[0].legend()
        plt.show()

    def plot_losses_metric_with_epoch(self):
        fig, ax = plt.subplots(nrows=1, ncols=2)
        ax[0].set_title("Minibatch Loss with Epoch")
        ax[1].set_title("Metric with Epoch")
        for phase in self.learner.phases:
            ax[0].plot(range(1, self.e_count+1), self.e_losses[phase], label=phase)
            ax[1].plot(range(1, self.e_count+1), self.e_metric[phase], label=phase)
        ax[0].legend()
        ax[0].set_xlabel('Epoch Number')
        ax[1].set_xlabel('Epoch Number')
        plt.show()
    
    def on_train_end(self):
        self.plot_losses_metric_with_iteration()
        self.plot_losses_metric_with_epoch()
        
