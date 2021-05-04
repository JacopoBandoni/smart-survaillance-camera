from skimage.metrics import structural_similarity as ssim
import cv2

imgA = cv2.imread("./frames-raspberry/2021-05-04--16-09-49-176982.jpeg")
imgB = cv2.imread("./frames-raspberry/2021-05-04--16-09-54-486203.jpeg")
res = ssim(imgA, imgB, multichannel=True)
print(res)