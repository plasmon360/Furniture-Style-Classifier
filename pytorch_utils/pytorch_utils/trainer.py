from .imports import *
from .callbacks import MyLrFinder, RecordMetric, Cyclic_LR


class learn():

    def __init__(self, data, model, optimizer, criterion, checkpoint_source):
        self.data = data
        self.model = model
        self.optimizer = optimizer
        self.loss_func = criterion
        self.checkpoint_source = Path(checkpoint_source) if not isinstance(checkpoint_source, Path) else checkpoint_source
        self.device = torch.device(
        "cuda:0" if torch.cuda.is_available() else "cpu")
        self.phases = ['train', 'val']

    def fit(self, epochs, callbacks):

        if not isinstance(callbacks, list):
            callbacks = [callbacks]

        [cb.on_train_begin() for cb in callbacks]

        self.model = self.model.to(self.device)

        for epoch in trange(epochs, desc='Epoch', leave=False):

            [cb.on_epoch_begin() for cb in callbacks]

            for self.phase in tqdm(self.phases, desc='Train/Val', leave=False):
                [cb.on_phase_begin() for cb in callbacks]

                if self.phase == 'train':
                    self.model.train()
                else:
                    self.model.eval()

                for batch_num, (inputs, targets) in enumerate(tqdm(self.data['dl'][self.phase], leave=False, desc='Batch')):


                    self.inputs = inputs.to(self.device)
                    self.targets = targets.to(self.device)
                    self.optimizer.zero_grad()

                    [cb.on_batch_begin() for cb in callbacks]

                    with torch.set_grad_enabled(self.phase == 'train'):
                        self.outputs = self.model(self.inputs)
                        self.batch_loss = self.loss_func(
                            self.outputs, self.targets)
                        if self.phase == 'train':
                            self.batch_loss.backward()
                            self.optimizer.step()
                        _, self.preds = torch.max(self.outputs, 1)

                    [cb.on_batch_end() for cb in callbacks]
                [cb.on_phase_end() for cb in callbacks]
            [cb.on_epoch_end() for cb in callbacks]

    def save(self, model_filename):
        '''
        Saves the current state of the model into a serializable file.
        '''
        if isinstance(checkpoint_filename, Path):
            # if the filename is path
            target = model_filename
        else:
            target = Path.joinpath(self.model_dir_path,
                                   f"{model_filename}.pth")
        print(f"Saving model at f{target}")
        torch.save(self.model.state_dict(), target)

    def load(self, checkpoint_filename):
        '''
        Loads a model state and loads in current model
        '''
        if isinstance(checkpoint_filename, Path):
            # if the filename is path
            source = model_filename
        else:
            source = Path.joinpath(self.model_dir_path,
                                   f'{model_filename}.pth')
        print(f"Loading model from {source}")
        self.model.load_state_dict(torch.load(source))

    def reset_model(self):
        '''
        Resets the model weights
        '''
        def weight_reset(m):
            m.reset_parameters()
        self.model.apply(weight_reset)

    def get_prediction(self, data):

        inference = {'preds': [], 'gt': [], 'probs': [], 'losses': []}
        inputs_temp = []

        self.loss_func.reduction = 'none'

        for inputs, targets in data['dl']['val']:
            inputs = inputs.to(self.device)
            targets = targets.to(self.device)
            self.model.to(self.device)
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(inputs)
                losses = self.loss_func(outputs, targets)

            _, preds = torch.max(outputs, 1)
            probs = torch.max(F.softmax(outputs, dim = 0))
            #inference['probs'].extend(probs.tolist())
            inference['preds'].extend(preds.tolist())
            inference['gt'].extend(targets.tolist())
            inference['losses'].extend(losses.tolist())
            inputs_temp.append(inputs)

        all_inputs = torch.cat(inputs_temp, dim=0)
        inference['all_inputs'] = all_inputs
        self.loss_func.reduction = 'mean'
        return inference

    def lr_finder(self, epochs, start_lr, stop_lr):
        # number of iterations = epochs *  len(train_dataset)/BATCH_SIZE
        num_iterations = epochs * len(self.data['dl']['train'])
        mylrfinder_callback = MyLrFinder(
            self, start_lr, stop_lr, num_iterations)
        self.fit(epochs, callbacks=mylrfinder_callback)
        mylrfinder_callback.plot_lr_with_iteration()
        mylrfinder_callback.plot_loss_vs_batch()

    def record_metric(self, epochs):
        record_callback = RecordMetric(self)
        self.fit(epochs, callbacks=[record_callback])
        record_callback.plot_losses_metric_with_iteration()
        record_callback.plot_losses_metric_with_epoch()

    def cyclic_lr(self, epochs, min_lr=1E-4, max_lr=1E-3, stepsize=100, policy='triangular'):
        clr_callback = Cyclic_LR(self, min_lr, max_lr, stepsize, policy)
        record_callback = RecordMetric(self)
        self.fit(epochs, callbacks=[clr_callback, record_callback])
        clr_callback.plot_lr_with_iteration()
        record_callback.plot_losses_metric_with_iteration()
        record_callback.plot_losses_metric_with_epoch()

    def unfreeze(self, num_layers, verbose=False):
        '''sets requires_grad = True for num_layers before any unfreezed layers
         If num_layers = -1 then all layers are unfreezed'''
        if num_layers == -1:
            for param in self.model.parameters():
                param.requires_grad = True
        else:
            # Count how many layers are frozen from the end .
            frozen = 0
            for param in self.model.parameters():
                if not param.requires_grad:
                    frozen += 1
            # Unfreeze layers from the last frozen layer towards the downstream.
            for index, (param_name, param) in enumerate(self.model.named_parameters()):
                if (index >= frozen-num_layers) and (index < frozen):
                    param.requires_grad = True

    def show_requires_grad(self):
        for param_name, param in self.model.named_parameters():
            print(param_name, param.requires_grad)


class Interpretration():

    def __init__(self, learn, data, inference):
        self.learn, self.data,self.inference= learn, data, inference 
    
    @classmethod
    def from_learner(cls,learn, data):
        inference = learn.get_predictions(data)
        return cls(learn, data, inference)

    def plot_top_N_losses(self,N=12):
        all_inputs = self.inference['all_inputs'] 
        top_N_losses = np.argsort(self.inference['losses'][-N:])
        ncols = 2
        nrows = int(np.ceil(N/ncols))
        fig, ax = plt.subplots(nrows, ncols, figsize=(8, 20))
        ax = ax.ravel()
        plt.suptitle("GT/PREDICTED/LOSS")
        for index, img in enumerate(top_N_losses[::-1]):
           if self.data['norm_stats']:
               mean, std = self.data['norm_stats']
               std = torch.tensor(std).to(self.learn.device)
               mean = torch.tensor(mean).to(self.learn.device)
               image = (all_inputs[img].mul(std[:, None, None]) + mean[:, None, None]).permute(1, 2, 0).cpu()
           else:
               image = all_inputs[img].permute(1, 2, 0).cpu()
           if image.shape[2] == 1: # if greyscale, make it color 
               image = image.squeeze()
               image = torch.stack([image]*3, dim = 2)
           ax[index].imshow(image)
           ax[index].set_title(f"{self.data['classes'][self.inference['gt'][img]]}/{self.data['classes'][self.inference['preds'][img]]}/{self.inference['losses'][img]:0.2f}")
           ax[index].axis('off')
       
