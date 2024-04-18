import os
import csv
import torch

from validate import validate
# from networks.resnet import resnet50
#-----------–-----------–-----------–--------
import torchvision.models as models
import torch.nn as nn
from networks.custom_models import *
from deepfake_detector import Detector, return_model
from data import create_dataloader
#-----------–-----------–-----------–--------
from options.test_options import TestOptions
from eval_config import *


def evaluation(model_path, name, opt):
    # Running tests
    model_name = os.path.basename(model_path).replace('.pth', '')
    rows = [["{} model testing on...".format(model_name)],
            ['testset', 'accuracy', 'avg precision', "f1 score", "roc score", "recall", "precision"]]

    print("{} model testing on...".format(model_name))
    
    opt.models = ["real", "PNDM", "DDPM", "LDM", "ProGAN", "DDIM", "StyleGAN_test", "VQGAN_test"]
    list_models = opt.models
    list_models.remove("real")
    
    model = return_model(opt.arch, add=opt.intermediate, dim=opt.intermediate_dim)
        
    state_dict = torch.load(model_path, map_location='cpu')
    model.load_state_dict(state_dict['model'])
    model.cuda()
    model.eval()
    
    for v_id, test_model in enumerate(list_models):
        opt.no_resize = True    # testing without resizing by default
        opt.models = [test_model, "real"]
        acc, ap, r_acc, f_acc, f1, auc, prec, recall, _, _ = validate(model, opt, "test_list")
        rows.append([test_model, acc, ap, f1, auc, prec, recall])
        print("({}) acc: {}; ap: {}; r_acc: {}; f_acc: {} f1: {}; roc_auc: {}; recall: {}; precision: {}".format(test_model, acc, ap, r_acc, f_acc, f1, auc, recall, prec))
        # ---------------------------------------------------------------------

    csv_name = results_dir + '/{}.csv'.format(name)
    with open(csv_name, 'w') as f:
        csv_writer = csv.writer(f, delimiter=',')
        csv_writer.writerows(rows)


def eval_multiple(path_list, opt):

    rows = [["{} model testing on...".format(opt.filename)],
            ['testset', 'accuracy', 'avg precision', "f1 score", "roc score", "recall", "precision"]]

    print("{} model testing on...".format(opt.filename))

    # ---------------------------------------------------------------------
    opt.models = ["real", "PNDM", "DDPM", "LDM", "ProGAN"]
    list_models = opt.models
    list_models.remove("real")

    detector = Detector(path_list)

    for v_id, test_model in enumerate(list_models):

        opt.models = [test_model, "real"]
        data_loader = create_dataloader(opt, "test_list")

        y_true, y_pred = detector.synth_real_detector(data_loader)
        acc, ap, r_acc, f_acc, f1, auc, prec, recall, _, _ = detector.return_metrics(y_true, y_pred)

        rows.append([test_model, acc, ap, f1, auc, prec, recall])
        print("({}) acc: {}; ap: {}; r_acc: {}; f_acc: {} f1: {}; roc_auc: {}; recall: {}; precision: {}".format(test_model, acc, ap, r_acc, f_acc, f1, auc, recall, prec))

    csv_name = results_dir + '/{}.csv'.format(opt.filename)
    with open(csv_name, 'w') as f:
        csv_writer = csv.writer(f, delimiter=',')
        csv_writer.writerows(rows)


if __name__ == "__main__":
    opt = TestOptions().parse(print_options=False)
    evaluation(opt.model_path, opt.filename, opt)
    # eval_multiple(["checkpoints/vgg16_inter#64_DDPM/model_epoch_best.pth", "checkpoints/vgg16_inter#64_PNDM/model_epoch_best.pth", "checkpoints/res50_inter#64_DDPM/model_epoch_best.pth", "checkpoints/efficient_inter#64_PNDM/model_epoch_best.pth", "checkpoints/efficient_inter#64_DDPM/model_epoch_best.pth"], opt)
