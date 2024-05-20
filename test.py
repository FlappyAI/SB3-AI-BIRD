import torch
import tensorflow as tf
import logging
logging.basicConfig(level=logging.DEBUG)


print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
print("")
print("")
print("")

print(tf.__version__)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

print("")
print("")
print("")
try:
    import tensorboard
    print("TensorBoard is successfully imported.")
except ImportError as e:
    print(f"Failed to import TensorBoard: {e}")