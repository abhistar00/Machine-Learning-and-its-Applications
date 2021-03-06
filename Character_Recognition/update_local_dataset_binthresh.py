# -*- coding: utf-8 -*-
"""
Created on Thu May 24 14:30:03 2018

@author: Swapnil Masurekar
"""

import sys
import numpy as np
import cv2
import os

def update_data_binthresh(image):
    # module level variables ##########################################################################
    MIN_CONTOUR_AREA = 100
    
    RESIZED_IMAGE_WIDTH = 20
    RESIZED_IMAGE_HEIGHT = 30
    
    ###################################################################################################
    
    imgTrainingNumbers = cv2.imread(image)            # read in training numbers image
    
    if imgTrainingNumbers is None:                          # if image was not read successfully
        print ("error: image not read from file \n\n")        # print error message to std out
        os.system("pause")                                  # pause so user can see error message
                                                      # and exit function (which exits program)
    
    
    
       
    imgGray = cv2.cvtColor(imgTrainingNumbers, cv2.COLOR_BGR2GRAY)          # get grayscale image
    imgBlurred = cv2.GaussianBlur(imgGray, (5,5), 0)                        # blur
    
                                                        # filter image from grayscale to black and white
#    imgThresh = cv2.adaptiveThreshold(imgBlurred,                           # input image
#                                      255,                                  # make pixels that pass the threshold full white
#                                      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,       # use gaussian rather than mean, seems to give better results
#                                      cv2.THRESH_BINARY_INV,                # invert so foreground will be white, background will be black
#                                      11,                                   # size of a pixel neighborhood used to calculate threshold value
#                                      2)                                    # constant subtracted from the mean or weighted mean
    ret,imgThresh = cv2.threshold(imgBlurred,127,255,cv2.THRESH_BINARY_INV)
    
    cv2.imshow("imgThresh", imgThresh)      # show threshold image for reference
    
    
    imgThreshCopy = imgThresh.copy()        # make a copy of the thresh image, this in necessary b/c findContours modifies the image
    
    imgContours, npaContours, npaHierarchy = cv2.findContours(imgThreshCopy,        # input image, make sure to use a copy since the function will modify this image in the course of finding contours
                                                 cv2.RETR_EXTERNAL,                 # retrieve the outermost contours only
                                                 cv2.CHAIN_APPROX_SIMPLE)           # compress horizontal, vertical, and diagonal segments and leave only their end points
    
                                # declare empty numpy array, we will use this to write to file later
                                # zero rows, enough cols to hold all image data
    npaFlattenedImages =  np.empty((0, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
    
    intClassifications = []         # declare empty classifications list, this will be our list of how we are classifying our chars from user input, we will write to file at the end
    
                                    # possible chars we are interested in are digits 0 through 9, put these in list intValidChars
    intValidChars = [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'),
                     ord('A'), ord('B'), ord('C'), ord('D'), ord('E'), ord('F'), ord('G'), ord('H'), ord('I'), ord('J'),
                     ord('K'), ord('L'), ord('M'), ord('N'), ord('O'), ord('P'), ord('Q'), ord('R'), ord('S'), ord('T'),
                     ord('U'), ord('V'), ord('W'), ord('X'), ord('Y'), ord('Z')]
    
    for npaContour in npaContours:                          # for each contour
        if cv2.contourArea(npaContour) > MIN_CONTOUR_AREA:          # if contour is big enough to consider
            [intX, intY, intW, intH] = cv2.boundingRect(npaContour)         # get and break out bounding rect
    
                                                # draw rectangle around each contour as we ask user for input
            cv2.rectangle(imgTrainingNumbers,           # draw rectangle on original training image
                          (intX, intY),                 # upper left corner
                          (intX+intW,intY+intH),        # lower right corner
                          (0, 0, 255),                  # red
                          2)                            # thickness
    
            imgROI = imgThresh[intY:intY+intH, intX:intX+intW]                                  # crop char out of threshold image
            imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))     # resize image, this will be more consistent for recognition and storage
            
            ret,imgROIResized = cv2.threshold(imgROIResized,127,255,cv2.THRESH_BINARY_INV)      # Again threshold the image as resizing affects threshold effects

            cv2.imshow("imgROI", imgROI)                    # show cropped out char for reference
            cv2.imshow("imgROIResized", imgROIResized)      # show resized image for reference
            cv2.imshow("training_numbers.png", imgTrainingNumbers)      # show training numbers image, this will now have red rectangles drawn on it
    
            intChar = cv2.waitKey(0)                     # get key press
    
            if intChar == 27:                   # if esc key was pressed
                sys.exit()                      # exit program
            
## For training all character remove this elif statement ----------------------
            elif intChar in intValidChars:      # else if the char is in the list of chars we are looking for . . .
    
                intClassifications.append(intChar)                                                # append classification char to integer list of chars (we will convert to float later before writing to file)
    
                npaFlattenedImage = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))  # flatten image to 1d numpy array so we can write to file later
                npaFlattenedImages = np.append(npaFlattenedImages, npaFlattenedImage, 0)                    # add current flattened impage numpy array to list of flattened image numpy arrays

    
    fltClassifications = np.array(intClassifications, np.float32)                   # convert classifications list of ints to numpy array of floats
    
    npaClassifications = fltClassifications.reshape((fltClassifications.size, 1))   # flatten numpy array of floats to 1d so we can write to file later
    
    print ("\n\ntraining complete !!\n")
    cv2.destroyAllWindows()             # remove windows from memory
    try:
        npaClassifications_og = np.loadtxt("classifications_binthresh.txt", np.float32)                  # read in training classifications
    except:
        print ("error, unable to open classifications_binthresh.txt, exiting program\n")
        os.system("pause")

    try:
        npaFlattenedImages_og = np.loadtxt("flattened_images_binthresh.txt", np.float32)                 # read in training images
    except:
        print ("error, unable to open flattened_images_binthresh.txt, exiting program\n")
        os.system("pause")

    
    
    npaFlattenedImages_loadable= np.append(npaFlattenedImages_og,npaFlattenedImages,axis=0) # adding new images to load in text file
    npaClassifications_loadable = np.append(npaClassifications_og,npaClassifications)  # adding new classifications to load in text file
    
    np.savetxt("classifications_binthresh.txt", npaClassifications_loadable)           # write flattened images to text file
    np.savetxt("flattened_images_binthresh.txt", npaFlattenedImages_loadable)          # write classifiactions to text file
    
    



###################################################################################################





