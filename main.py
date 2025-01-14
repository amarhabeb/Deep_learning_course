import argparse
import data_set
import model
import torch
import torch.nn as nn

parser = argparse.ArgumentParser()

parser.add_argument("-t", "--train", nargs='?', help="train NN for FashionMinst dataset", const=True)
parser.add_argument("-e", "--test", nargs='?', help="test NN for FashionMinst dataset", const=True)
parser.add_argument("-f", "--TFGSM", nargs='?',  help="run TFGSM adversial attack", const=True)
parser.add_argument("-d", "--DEEPFOOL", nargs='?',  help="run Deep fool adversial attack", const=True)
parser.add_argument("-s", "--defense", nargs='?',  help="run Deep fool adversial attack", const=True)
parser.add_argument("-p", "--DeepDefense", nargs='?',  help="run deepfool defence", const=True)
parser.add_argument("-n", "--encoder", nargs='?',  help="run encoder defence", const=True)




args = parser.parse_args()

trained_model = None
train_loader, val_loader, test_loader = data_set.load_dataset()
fashion_model = model.Fashion_MNIST_CNN()
device = torch.device('cpu')
if torch.cuda.is_available():
    device = torch.device('cuda')
fashion_model.to(device)
X, Y = next(iter(test_loader))

if args.train:
    import train
    trained_model = train.train_model(model=fashion_model, train_loader=train_loader, validation_loader=val_loader, epochs=20, learning_rate=0.001, optimizer=torch.optim.Adam(fashion_model.parameters(), lr=0.001), loss_function=nn.CrossEntropyLoss(), device=device, patience=5)
if args.test:
    import test
    test.test_model(model=trained_model, test_loader=test_loader, epochs=1, loss_function=nn.CrossEntropyLoss(), device=device)
if args.TFGSM:
    import tfgsm_attack
    attack = tfgsm_attack.FGSMAttack(trained_model, [0.5], test_loader, device, Y.to(device))
    attack.run()
if args.DEEPFOOL:
    import deep_fool
    deep_fool_instance = deep_fool.DeepFoolAttack(model=trained_model, device= device,max_iter=4)
    deep_fool_instance.run(test_loader=test_loader)
if args.DeepDefense:
    import deep_fool_train_defnse
    import deep_fool
    fashion_deep_model = model.Fashion_MNIST_CNN()
    trained_model_defense = deep_fool_train_defnse.train_model(model=fashion_deep_model, train_loader=train_loader,validation_loader=val_loader, epochs=2, learning_rate=0.001, optimizer=torch.optim.Adam(fashion_model.parameters(), lr=0.001), loss_function=nn.CrossEntropyLoss(), device=device, patience=5)
    attack = deep_fool.DeepFoolAttack(model=trained_model_defense, device= device)
    attack.evaluate_attack(test_dataloader=test_loader,model=trained_model_defense)
if args.defense:
    import train_defense_tfgsm
    import tfgsm_attack
    fashion_model_defensed = model.Fashion_MNIST_CNN()
    trained_model_defensed = train_defense_tfgsm.train_model(model=fashion_model, train_loader=train_loader, validation_loader=val_loader, epochs=20, learning_rate=0.001, optimizer=torch.optim.Adam(fashion_model.parameters(), lr=0.001), loss_function=nn.CrossEntropyLoss(), device=device, Y=Y.to(device), patience=5)
    attack = tfgsm_attack.FGSMAttack(trained_model_defensed, [0.5], test_loader, device, Y.to(device))
    attack.run()
if args.encoder:
    import encoder_decoder
    import train
    import deep_fool
    encoder = encoder_decoder.ConvAutoencoder()
    encoder_model = encoder_decoder.Fashion_MNIST_CNN(encoder)
    encoder_model.to(device)
    encoder_model = train.train_model(model=encoder_model, train_loader=train_loader, validation_loader=val_loader, epochs=20, learning_rate=0.001, optimizer=torch.optim.Adam(fashion_model.parameters(), lr=0.001), loss_function=nn.CrossEntropyLoss(), device=device, patience=5)
    attack = deep_fool.DeepFoolAttack(model=encoder_model, device=device,max_iter=4)
    attack.evaluate_attack(test_dataloader=test_loader, model=encoder_model)


