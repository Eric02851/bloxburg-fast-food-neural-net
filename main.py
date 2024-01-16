import pyautogui
import numpy as np
import cv2 as cv
import time
import os
from pynput import mouse
import csv
import threading

burger4min = 865
burger4max = 1691

burger3min = 965
burger3max = 1587

burger2min = 1065
burger2max = 1490

windowMiddle = 415
minY = 410
maxY = 550

csvHeader = ["imageName", "labels"]
imageFolder = r"C:\Users\ziggy\Documents\GitHub\bloxburg-fast-food-neural-net\labledData\images"
csvFolder = r"C:\Users\ziggy\Documents\GitHub\bloxburg-fast-food-neural-net\labledData\csv"

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
    MenuButton(540, 593, 2130, 2265, "cheese"),
    MenuButton(615, 695, 2069, 2185, "patty"),
    MenuButton(596, 698, 2203, 2328, "veggiePatty"),
    MenuButton(704, 810, 2128, 2265, "tomato"),
    MenuButton(827, 911, 2132, 2269, "lettuce"),
    MenuButton(323, 412, 2288, 2376, "undo")
]

sideOptions = [
    MenuButton(425, 567, 2033, 2179, "fries"),
    MenuButton(598, 740, 2033, 2179, "sticks"),
    MenuButton(768, 911, 2033, 2179, "rings")
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

order = {
    "done": False,
    "valid": False,
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

sideOptions += sizeOptions
drinkOptions += sizeOptions
catagory = catagoryOptions[0]

def padImage(screenshot, targetWidth):
    padWidth = targetWidth - screenshot.shape[1]

    padLeft = padWidth // 2
    padRight = padWidth - padLeft

    return np.pad(screenshot, ((0, 0), (padLeft, padRight), (0, 0)), mode='constant', constant_values=255)

def displayImg(screenshot):
    cv.imshow('screenshot', screenshot)
    cv.waitKey()
    cv.destroyAllWindows()

def getBurger(screenshot):
    if np.array_equal(screenshot[windowMiddle, burger4min], [255, 255, 255]):
        screenshot = screenshot[minY:maxY, burger4min:burger4max]
        print("burger4")
        return padImage(screenshot, 826)

    if np.array_equal(screenshot[windowMiddle, burger3min], [255, 255, 255]):
        screenshot = screenshot[minY:maxY, burger3min:burger3max]
        print("burger3")
        return padImage(screenshot, 826)

    screenshot = screenshot[minY:maxY, burger2min:burger2max]
    print("burger2/1")
    return padImage(screenshot, 826)

def getSideAndDrink(screenshot):
    screenshot = screenshot[minY:maxY, burger2min:burger2max]
    return padImage(screenshot, 826)

def takeScreenshot():
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)

    return screenshot

def getOrder():
    print("Waiting for customer")
    screenshot = takeScreenshot()
    while not np.array_equal(screenshot[320, 1412], [255, 255, 255]):
        time.sleep(0.1)
        screenshot = takeScreenshot()

    time.sleep(0.5)
    burger = getBurger(screenshot)
    print("Got burger")

    time.sleep(5)
    screenshot = takeScreenshot()
    side = getSideAndDrink(screenshot)
    print("Got side")

    #time.sleep(2.5)
    time.sleep(2)
    screenshot = takeScreenshot()
    drink =  []
    if np.array_equal(screenshot[320, 1412], [255, 255, 255]):
        print("Got drink")
        drink = getSideAndDrink(screenshot)
        time.sleep(3)

    return {"burger": burger, "side": side, "drink": drink}

def onClick(x, y, mouseButton, pressed):
    global catagory
    global order

    if pressed and mouseButton == mouseButton.left:
        #print(f"Mouse clicked at ({x}, {y}) with button {mouseButton}")
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
                            order[catagory.name]["size"] = b.name[0].upper()

                print(order)
                break

        for b in catagoryOptions:
            if b.clicked(x, y):
                if b.name == "done": #check here if the order is good or not
                    time.sleep(1.5)
                    while True:
                        print("Checking validity")
                        screenshot = takeScreenshot()
                        if np.array_equal(screenshot[600, 2267], [74, 175, 101]):
                            print("Valid")
                            order["valid"] = True
                            break
                        elif np.array_equal(screenshot[600, 2267], [39, 65, 170]):
                            print("Invalid")
                            break
                        time.sleep(0.1)

                    order["done"] = True
                    print("Done")
                    catagory = catagoryOptions[0]
                else: catagory = b
                break

def getImageIds():
    imageIds = {"burger": 0, "side": 0, "drink": 0}

    for i in imageIds:
        imageList = os.listdir(f"{imageFolder}/{i}")
        imageList = sorted(imageList, key=lambda x: int(x.split('.')[0][5:]))

        if len(imageList) != 0:
            imageIds[i] = int(imageList[-1].split('.')[0][5:]) + 1

    return imageIds

def writeImages(images, imageIds):
    for i in images:
        if not len(images[i]): continue
        imagePath = f"{imageFolder}/{i}/image{imageIds[i]}.png"
        cv.imwrite(imagePath, images[i])
        imageIds[i] += 1

    return imageIds

def writeCSVs(images, imageIds, order):
    for i in images:
        row = [f"image{imageIds[i]}.png", ""]
        if i == "burger":
            j = 0
            items = order["burger"]

            while j < len(items):
                if items.count(items[j]) > 1:
                    duplicate = items[j]
                    while j < len(items) and items[j] == duplicate:
                        j += 1
                    row[1] += f",{duplicate}2"
                else:
                    row[1] += f",{items[j]}"
                    j += 1

            row[1] = row[1][1:]
        else:
            if not len(images[i]): continue
            row[1] = order[i]["name"] + order[i]["size"]

        csvPath = f"{csvFolder}/{i}.csv"
        with open(csvPath, 'a', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)

def listenerThread():
    with mouse.Listener(on_click=onClick) as listener:
        listener.join()

def main():
    imageIds = getImageIds()
    print(imageIds["burger"], imageIds["side"], imageIds["drink"])

    threading.Thread(target=listenerThread).start()

    while True:
        images = getOrder()

        while not order["done"]:
            time.sleep(0.5)

        if order["valid"]:
            writeCSVs(images, imageIds, order)
            imageIds = writeImages(images, imageIds)

        order["done"] = False
        order["valid"] = False
        order["burger"].clear()

        for i in order["side"]: order["side"][i] = ""
        for i in order["drink"]: order["drink"][i] = ""
        time.sleep(1)

main()
