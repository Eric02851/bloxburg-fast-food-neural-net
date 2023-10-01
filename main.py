import pyautogui
import numpy as np
import cv2 as cv
import time
import os
import pydirectinput

centerPlus = (475, 1270) #For 2 and 4 items
leftPlus = (476, 1160) #For 3 items
plusColor = [100, 100, 100]

plusSideOffset = 205
plusArmOsset = 22 #There should be no black in image on the sides

maxYOffset = 63
minYOffset = 77

y1 = 0
y2 = 0

drinkFries = [(412, 1199),(552, 1360)]

unlabledFolder = r"C:\Users\ziggy\Documents\GitHub\bloxburg-fast-food-neural-net\unlabled"

def displayImg(screenshot):
    #screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
    cv.imshow('screenshot', screenshot)
    cv.waitKey()
    cv.destroyAllWindows()

def getMiddle(screenshot, plusCords):
        middle = False
        j = 0
        for j in range(20):
            if np.allclose(screenshot[plusCords[0], plusCords[1] + j], plusColor, atol=10):
                for k in range(18):
                    if np.allclose(screenshot[plusCords[0] + k, plusCords[1] + j - 1], plusColor, atol=10):
                        middle = [plusCords[0] + k, plusCords[1] + j]
                        return middle

def getLeftItem(screenshot, middle, itemOffset):
    x1 = middle[1] - plusSideOffset * (itemOffset + 1) + plusArmOsset
    x2 = middle[1] - plusSideOffset * itemOffset - plusArmOsset
    return screenshot[y1:y2, x1:x2]

def getRightItem(screenshot, middle, itemOffset):
    x1 = middle[1] + plusSideOffset * itemOffset + plusArmOsset
    x2 = middle[1] + plusSideOffset * (itemOffset + 1) - plusArmOsset
    return screenshot[y1:y2, x1:x2]

def getBurger(screenshot):
    global y1, y2

    itemCount = 0
    middle = getMiddle(screenshot, centerPlus)
    if middle:
        plusToLeft = np.allclose(screenshot[middle[0], middle[1] + plusSideOffset], plusColor, atol=10)
        itemCount = 4 if plusToLeft else 2
    else:
        middle = getMiddle(screenshot, leftPlus)
        itemCount = 3

    if not middle:
        return []

    y1 = middle[0] - minYOffset
    y2 = middle[0] + maxYOffset

    items = []
    if itemCount == 4:
        items.append(getLeftItem(screenshot, middle, 1))
        items.append(getLeftItem(screenshot, middle, 0))
        items.append(getRightItem(screenshot, middle, 0))
        items.append(getRightItem(screenshot, middle, 1))

    elif itemCount == 3:
        items.append(getLeftItem(screenshot, middle, 0))
        items.append(getRightItem(screenshot, middle, 0))
        items.append(getRightItem(screenshot, middle, 1))

    else:
        items.append(getLeftItem(screenshot, middle, 0))
        items.append(getRightItem(screenshot, middle, 0))

    return items

def getSideAndDrink(screenshot):
    return screenshot[drinkFries[0][0]:drinkFries[1][0], drinkFries[0][1]:drinkFries[1][1]]

def takeScreenshot():
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)

    return screenshot

def getOrder():
    screenshot = takeScreenshot()

    print("Waiting for customer")
    while not np.array_equal(screenshot[320, 1412], [255, 255, 255]):
        time.sleep(0.1)
        screenshot = takeScreenshot()

    items = getBurger(screenshot)
    print(f"Burger: {len(items)}")
    if len(items) == 0:
        print("Burger failed")

        pydirectinput.press('space')
        time.sleep(3)
        pydirectinput.press('e')
        return getOrder()

    time.sleep(5)
    screenshot = takeScreenshot()

    side = getSideAndDrink(screenshot)
    print("Side")

    time.sleep(2.5)
    screenshot = takeScreenshot()

    drink =  []
    if np.array_equal(screenshot[320, 1412], [255, 255, 255]):
        print("Drink")
        drink = getSideAndDrink(screenshot)
        time.sleep(3)

    print("Done", end="\n\n")
    return items, side, drink

def getImageId(subfolder):
    imageList = os.listdir(f"{unlabledFolder}/{subfolder}")
    imageList = sorted(imageList, key=lambda x: int(x.split('.')[0]))

    id = 0
    if len(imageList) != 0:
        id = int(imageList[-1].split('.')[0]) + 1

    return id

def main():
    burgerId = getImageId("burgers")
    sideId = getImageId("sides")
    drinkId = getImageId("drinks")
    print(burgerId, sideId, drinkId)

    while True:
        burgerItems, side, drink = getOrder()

        for i in range(len(burgerItems)):
            imagePath = f"{unlabledFolder}/burgers/{burgerId}.png"
            cv.imwrite(imagePath, burgerItems[i])
            burgerId += 1

        imagePath = f"{unlabledFolder}/sides/{sideId}.png"
        cv.imwrite(imagePath, side)
        sideId += 1

        if len(drink):
            imagePath = f"{unlabledFolder}/drinks/{drinkId}.png"
            cv.imwrite(imagePath, drink)
            drinkId += 1

        pydirectinput.press('space')
        time.sleep(1)
        pydirectinput.press('e')

main()
