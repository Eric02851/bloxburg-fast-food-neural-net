import pyautogui
import numpy as np
import cv2 as cv
import time
import os
import pydirectinput
from pynput import mouse

#maxYOffset = 63
#minYOffset = 77

burger4min = 865
burger4max = 1691

burger3min = 965
burger3max = 1587

burger2min = 1065
burger2max = 1490

minY = 405
maxY = 545

windowMiddle = 415

drinkFries = [(412, 1199),(552, 1360)]
unlabledFolder = r"C:\Users\ziggy\Documents\GitHub\bloxburg-fast-food-neural-net\unlabled"

def padImage(screenshot, targetWidth):
    padWidth = targetWidth - screenshot.shape[1]

    padLeft = padWidth // 2
    padRight = padWidth - padLeft

    return np.pad(screenshot, ((0, 0), (padLeft, padRight), (0, 0)), mode='constant', constant_values=255)

def displayImg(screenshot):
    #screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
    cv.imshow('screenshot', screenshot)
    cv.waitKey()
    cv.destroyAllWindows()

def getBurger(screenshot):
    if np.array_equal(screenshot[windowMiddle, burger4min], [255, 255, 255]):
        screenshot = screenshot[minY:maxY, burger4min:burger4max]
        print("burger4")

        padded_screenshot = padImage(screenshot, 826)
        displayImg(padded_screenshot)
    elif np.array_equal(screenshot[windowMiddle, burger3min], [255, 255, 255]):
        screenshot = screenshot[minY:maxY, burger3min:burger3max]
        print("burger3")

        padded_screenshot = padImage(screenshot, 826)
        displayImg(padded_screenshot)
    else:
        screenshot = screenshot[minY:maxY, burger2min:burger2max]
        print("burger2/1")

        padded_screenshot = padImage(screenshot, 826)
        displayImg(padded_screenshot)


def getSideAndDrink(screenshot):
    return screenshot[minY:maxY, burger2min:burger2max]

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

    time.sleep(0.5)
    burger = getBurger(screenshot)
    print("got burger")

    time.sleep(5)
    screenshot = takeScreenshot()

    side = getSideAndDrink(screenshot)
    print("Got side")

    time.sleep(2.5)
    screenshot = takeScreenshot()

    drink =  []
    if np.array_equal(screenshot[320, 1412], [255, 255, 255]):
        print("Got drink")
        drink = getSideAndDrink(screenshot)
        time.sleep(3)

    print("Done", end="\n\n")
    return burger, side, drink

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
        time.sleep(2)
        pydirectinput.press('e')

#main()

#screenshot = takeScreenshot()
#side = getSideAndDrink(screenshot)
#displayImg(side)
#print("Side")
#getBurger(screenshot)

class MenuButton:
    def __init__(self, minY, maxY, minX, maxX, name, subButtons = None):
        self.minY = minY
        self.maxY = maxY
        self.minX = minX
        self.maxX = maxX
        self.name = name

        self.subButtons = subButtons

    def clicked(self, x, y):
        if y >= self.minY and y <= self.maxY and x >= self.minX and x <= self.maxX:
            return True
        return False

burgerOptions = [
    MenuButton(423, 504, 2132, 2272, "onion"),
    MenuButton(540, 585, 2130, 2265, "cheese"),
    MenuButton(615, 695, 2069, 2185, "patty"),
    MenuButton(596, 698, 2203, 2328, "vegiePatty"),
    MenuButton(704, 810, 2128, 2265, "tomato"),
    MenuButton(827, 911, 2132, 2269, "lettuce"),
    MenuButton(323, 412, 2288, 2376, "undo")
]

sideOptions = [
    MenuButton(425, 567, 2033, 2179, "fries"),
    MenuButton(598, 740, 2033, 2179, "mozzarellaSticks"),
    MenuButton(768, 911, 2033, 2179, "onionRings")
]

drinkOptions = [
    MenuButton(425, 567, 2033, 2179, "soda"),
    MenuButton(598, 740, 2033, 2179, "juice"),
    MenuButton(768, 911, 2033, 2179, "shake")
]

sizeOptions = [
    MenuButton(425, 567, 2218, 2364, "small"),
    MenuButton(598, 740, 2218, 2364, "medium"),
    MenuButton(768, 911, 2218, 2364, "large")
]

catagoryOptions = [
    MenuButton(375, 475, 2411, 2509, "burger", burgerOptions),
    MenuButton(538, 635, 2411, 2509, "side", sideOptions),
    MenuButton(701, 797, 2411, 2509, "drink", drinkOptions),
    MenuButton(861, 960, 2411, 2509, "done")
]

sideOptions += sizeOptions
drinkOptions += sizeOptions

catagory = catagoryOptions[0]
order = {
    "burger": [],
    "side": {
        "name": "",
        "size": ""
    },
    "drink": {
        "name": "",
        "size": ""
    }
}

def on_click(x, y, mouseButton, pressed):
    global catagory
    global order

    if pressed and mouseButton == mouseButton.left:
        for b in catagory.subButtons:
            if b.clicked(x, y):
                if catagory.name == "burger":
                    if b.name == "undo":
                        if order[catagory.name]: order[catagory.name].pop()
                    else:
                        order[catagory.name].append(b.name)
                else:
                    if b.name != "small" and b.name != "medium" and b.name != "large":
                        if b.name == order[catagory.name]["name"]:
                            order[catagory.name]["name"] = ""
                            order[catagory.name]["size"] = ""
                        else:
                            order[catagory.name]["name"] = b.name
                    else:
                        if order[catagory.name]["name"]:
                            order[catagory.name]["size"] = b.name

                print(order)
                break

        for b in catagoryOptions:
            if b.clicked(x, y):
                if b.name == "done":
                    print(order)

                    order["burger"].clear()
                    for i in order["side"]: order["side"][i] = ""
                    for i in order["drink"]: order["drink"][i] = ""

                    print(order)
                    catagory = catagoryOptions[0]
                else:
                    catagory = b

                print(b.name)
                break

        #print(f"Mouse clicked at ({x}, {y}) with button {mouseButton}")

# Start listening to mouse events
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
