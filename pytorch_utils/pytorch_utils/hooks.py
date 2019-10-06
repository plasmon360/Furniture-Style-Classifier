def hook_func0(self, input, output):
    "This is a dummy hook func which returns input and output"
    return input, output

    
class Hook():
    '''
    This is hook context manager which is used to get the input and output and their shapes
    for a net module
    usage:
    
    import torch
    with Hook(mymodel) as hook:
        dummy_img=torch.randn(2, 3, 64, 64)
        _=mymodel(dummy_img)

    print(hook.output_shape)
    print(hook.output)
    
    '''
    def __init__(self, module, hook_func=hook_func0, forward=True):
        if forward:
            self.handle = module.register_forward_hook(self.hook_func_wrapper)
        else:
            self.handle = module.register_backward_hook(self.hook_func_wrapper)
        self.hook_func = hook_func
        self.remove_status = False
        
    def hook_func_wrapper(self, module, input, output):
        self.input, self.output = self.hook_func(module, input, output)
         
    def remove(self):
        if not self.remove_status:
            self.handle.remove()
            self.remove_status = True
    
    @property
    def output_shape(self):
        return self.output.data.shape

    @property
    def input_shape(self):
        return self.input[0].shape
   
    def __enter__(self): return self
        
    def __exit__(self, type, value, traceback): 
        self.remove()




