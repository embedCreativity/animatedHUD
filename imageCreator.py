#!/usr/bin/env python3

import cv2
import numpy as np

def getFrameSize(image):
    img = cv2.imread(image, cv2.IMREAD_UNCHANGED)
    shape = img.shape
    return (shape[0], shape[1]) # row/col - discard alpha if present


class ImageCreator:

    background_img = ''
    left_foreground_img = ''
    left_alpha_channel = []
    left_matte_row = []
    left_offsets = ()
    right_offsets = ()
    right_foreground_img = ''
    right_alpha_channel = []
    right_matte_row = []
    rows = 0
    cols = 0
    channels = 0

    def __init__(self, left_foreground_img, left_offsets, right_foreground_img, right_offsets, background_img):
        # grab the background layer
        self.background_img = cv2.imread(background_img, cv2.IMREAD_UNCHANGED)
        self.background_img = self.background_img.astype(float) # convert data type to float
        self.background_img = self.background_img[:,:,:3] # strip out alpha channel

        # !!! all images are assumed to be the same size !!!
        self.rows,self.cols,self.channels = self.background_img.shape

        # grab the left foreground layer
        self.left_foreground_img = cv2.imread(left_foreground_img, cv2.IMREAD_UNCHANGED)
        self.left_alpha_channel = self.left_foreground_img[:,:,3] # grab the alpha channel from the rotated image
        self.left_foreground_img = self.left_foreground_img[:,:,:3] # strip out alpha channel
        # create template row for creating an rgb mask that is set to alpha value
        self.left_matte_row = np.ones(shape=(self.rows,self.cols,1))
        self.left_offsets = left_offsets

        # grab the right foreground layer
        self.right_foreground_img = cv2.imread(right_foreground_img, cv2.IMREAD_UNCHANGED)
        self.right_alpha_channel = self.right_foreground_img[:,:,3] # grab the alpha channel from the rotated image
        self.right_foreground_img = self.right_foreground_img[:,:,:3] # strip out alpha channel
        # create template row for creating an rgb mask that is set to alpha value
        self.right_matte_row = np.ones(shape=(self.rows,self.cols,1))
        self.right_offsets = right_offsets

    def createImage(self, left_rotation, right_rotation):

        ####### Left Foreground First ####################
        # create a rotation matrix
        M = cv2.getRotationMatrix2D((self.cols/2,self.rows/2),(-1 * left_rotation),1) # NOTE: a negative (-1*value) rotation produces clockwise rotation
        # create a translation matrix
        TM = np.float32([[1,0,self.left_offsets[0]], [0,1,self.left_offsets[1]]])
        # apply that rotation
        rotated_left_alpha_channel = cv2.warpAffine(self.left_alpha_channel,M,(self.cols,self.rows)) # rotate the alpha layer
        left_rotated_foreground = cv2.warpAffine(self.left_foreground_img,M,(self.cols,self.rows)) # rotate the foreground layer
        # translate the rotated image
        rotated_left_alpha_channel = cv2.warpAffine(rotated_left_alpha_channel, TM, (self.cols, self.rows))
        left_rotated_foreground = cv2.warpAffine(left_rotated_foreground, TM, (self.cols, self.rows))
        left_rotated_foreground = left_rotated_foreground.astype(float) # convert data type to float

        # mask it with alpha
        left_matte_row_mask = np.multiply(rotated_left_alpha_channel, self.left_matte_row.reshape(1,self.rows,self.cols)[:,:,0]).reshape(self.rows,self.cols,1)
        # create rows,cols matrix with rgb channels set to alpha value for mask
        left_alpha_matte = np.concatenate([left_matte_row_mask, left_matte_row_mask, left_matte_row_mask], axis=2)
        left_alpha_matte = left_alpha_matte.astype(float)/255 # normalize rotated alpha channel from 0 - 255
        left_foreground = cv2.multiply(left_alpha_matte, left_rotated_foreground) # multiply the foreground with the alpha matte

        ####### Right Foreground Next ####################
        # create a rotation matrix
        M = cv2.getRotationMatrix2D((self.cols/2,self.rows/2),(right_rotation),1) # NOTE: a positive (value) rotation produces counter-clockwise rotation
        # create a translation matrix
        TM = np.float32([[1,0,self.right_offsets[0]], [0,1,self.right_offsets[1]]])
        # apply that rotation
        rotated_right_alpha_channel = cv2.warpAffine(self.right_alpha_channel,M,(self.cols,self.rows)) # rotate the alpha layer
        right_rotated_foreground = cv2.warpAffine(self.right_foreground_img,M,(self.cols,self.rows)) # rotate the foreground layer
        # translate the rotated image
        rotated_right_alpha_channel = cv2.warpAffine(rotated_right_alpha_channel, TM, (self.cols, self.rows))
        right_rotated_foreground = cv2.warpAffine(right_rotated_foreground, TM, (self.cols, self.rows))
        right_rotated_foreground = right_rotated_foreground.astype(float) # convert data type to float

        # mask it with alpha
        right_matte_row_mask = np.multiply(rotated_right_alpha_channel, self.right_matte_row.reshape(1,self.rows,self.cols)[:,:,0]).reshape(self.rows,self.cols,1)
        # create rows,cols matrix with rgb channels set to alpha value for mask
        right_alpha_matte = np.concatenate([right_matte_row_mask, right_matte_row_mask, right_matte_row_mask], axis=2)
        right_alpha_matte = right_alpha_matte.astype(float)/255 # normalize rotated alpha channel from 0 - 255
        right_foreground = cv2.multiply(right_alpha_matte, right_rotated_foreground) # multiply the foreground with the alpha matte


        # merge left image with background
        background = cv2.multiply(1.0 - left_alpha_matte, self.background_img)
        leftMerge = cv2.add(left_foreground, background)

        # merge right image with background
        background = cv2.multiply(1.0 - right_alpha_matte, leftMerge)
        outImage = cv2.add(right_foreground, background)

        return outImage
