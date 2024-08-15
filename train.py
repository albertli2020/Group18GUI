from cellpose import models, io, train
import os

path = '/Users/albert2/Desktop/masks'

io.logger_setup()

output = io.load_train_test_data(path, mask_filter='_seg.npy', look_one_level_down=False)
images,labels, image_names, _, _, _ = output

model = models.CellposeModel(model_type="nuclei")
model_path = train.train_seg(model.net, train_data=images, train_labels=labels,
                             channels=[1,2], normalize=True,
                             weight_decay=1e-4, SGD=True, learning_rate=0.1,
                             n_epochs=100, model_name='astrocyte_nuclei')
