#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [Microscope] Class for controlling microscope
# @author   Daeho Kim (r4576@kist.re.kr)
"""
This module provides a Python interface to the CN_X4_500 microscope for casting inspection in the Electrochemical Measurement Module.
The implementation supports real-time camera connection, single-image acquisition,
inspection of the captured frame, and result logging based on image analysis.
The inspection result is classified as either Success or Failure and is delivered through the device operation message.
"""
import cv2
import os, sys
import numpy as np
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from Log.Logging_Class import NodeLogger
from Device_Exception import DeviceError
from datetime import datetime


class CN_X4_500(DeviceError):

    def __init__(self, logger_obj, device_name="CN_X4_500", camera_index=0):
        self.logger_obj = logger_obj
        self.camera_index = camera_index
        self.device_name = device_name
        self.info = {
        }
        self.cap = None

    def heartbeat(self,):
        # self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        # connection = self.cap.isOpened()
        # error_dict = self.checkStatusError(True, connection)
        debug_device_name = "{} ({})".format(self.device_name, "heartbeat")
        debug_msg = "Hello World!! Succeed to connection to main computer!"
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)

        return_res_msg = "[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg

    def _get_save_directory(self):
        current_date = datetime.now().strftime("%Y%m%d")
        directory_path = f'Microscope/data/{current_date}'
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return directory_path

    def _start_capture(self, filename):
        # Open USB camera using DirectShow backend
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)

        # Set camera frame width and height (1980x1080)
        self.cap.set(3, 1980)  # Frame width setting
        self.cap.set(4, 1080)  # Frame height setting

        # Create resizable window
        cv2.namedWindow('Microscope', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Microscope', 640, 480)

    def _stop_capture(self):
        # Release resources
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()

    def _detect_circles(self, image, black_threshold=150, fail_ratio_threshold=0.01):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=30,
            param1=100,
            param2=25,
            minRadius=215,
            maxRadius=219
        )

        if circles is None:
            return image, 0.0, True, "No circles were detected"

        circles = np.uint16(np.around(circles))
        largest_circle = max(circles[0, :], key=lambda c: c[2])
        x, y, radius = largest_circle

        result_image = image.copy()
        cv2.circle(result_image, (x, y), 1, (0, 100, 100), 3)
        cv2.circle(result_image, (x, y), radius, (0, 255, 0), 3)

        big_radius = radius
        small_radius = 102
        gray_color = [128, 128, 128]

        mask = np.zeros_like(gray)
        cv2.circle(mask, (x, y), big_radius, 255, thickness=-1)
        cv2.circle(mask, (x, y), small_radius, 0, thickness=-1)

        region_between_circles = cv2.bitwise_and(gray, gray, mask=mask)

        dark_pixels = (mask == 255) & (region_between_circles < black_threshold)
        result_image[dark_pixels] = gray_color

        masked_gray_pixels = np.sum(dark_pixels)
        total_pixels = np.sum(mask == 255)
        masked_pixel_ratio = masked_gray_pixels / total_pixels if total_pixels != 0 else 0.0

        failed = masked_pixel_ratio > fail_ratio_threshold
        if failed:
            cv2.circle(result_image, (x, y), small_radius, (0, 0, 255), 2)
        else:
            cv2.circle(result_image, (x, y), small_radius, (0, 255, 0), 2)

        return result_image, masked_pixel_ratio, failed, "Inspection completed"

    def inspection(self, filename, black_threshold=150, fail_ratio_threshold=0.01, save_result=True):
        debug_device_name = "{} ({})".format(self.device_name, "inspection")

        ret, frame = self.cap.read()
        error_dict = self.checkStatusError(True, ret)
        msg = "Inspection Capture! --> Operating : {}, Status : {}".format(bool(ret), error_dict)
        self.logger_obj.debug(debug_device_name, msg)

        if not ret or frame is None:
            raise RuntimeError("Failed to capture image from microscope camera")

        cv2.imshow('Microscope', frame)
        cv2.waitKey(1)

        inspected_image, masked_pixel_ratio, failed, detail_msg = self._detect_circles(
            frame,
            black_threshold=black_threshold,
            fail_ratio_threshold=fail_ratio_threshold
        )

        if save_result:
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            directory_path = self._get_save_directory()
            casting_condition = "Failure" if failed else "Success"
            image_path = f"{directory_path}/{current_time}_{filename}_{casting_condition}_{masked_pixel_ratio:.2%}.jpg"
            cv2.imwrite(image_path, inspected_image)
            self.logger_obj.debug(debug_device_name, f"Inspection image saved: {image_path}")

        self.logger_obj.debug(
            debug_device_name,
            "Inspection Result --> {}, masked_pixel_ratio: {:.4f}, msg: {}".format(
                casting_condition, masked_pixel_ratio, detail_msg
            )
        )

        return {
            "status": casting_condition,
            "masked_pixel_ratio": masked_pixel_ratio,
            "detail_msg": detail_msg,
            "image": inspected_image,
        }

    def operate(self, filename, duration_seconds, mode_type="virtual"):
        debug_device_name = "{} ({})".format(self.device_name, mode_type)

        if mode_type == "real":
            msg = "Microscope Start ... single image inspection mode"
            self.logger_obj.debug(debug_device_name, msg)

            self._start_capture(filename=filename)
            try:
                inspection_result = self.inspection(filename=filename)
            finally:
                self._stop_capture()

            casting_condition = inspection_result["status"] 
            inspection_msg = "Inspection : casting {}".format(casting_condition)

            self.logger_obj.debug(device_name=debug_device_name, debug_msg=inspection_msg)
            res_msg = debug_device_name + " : " + inspection_msg
            
    
        elif mode_type == "virtual":
            msg = "Inspection : Casting Success"
            casting_condition = "Success"
            self.logger_obj.debug(debug_device_name, msg)
            res_msg = debug_device_name + " : " + msg
        
        return res_msg, casting_condition


if __name__ == '__main__':
    NodeLogger_obj = NodeLogger(
        platform_name="Electrochemical Analysis",
        setLevel="DEBUG",
        SAVE_DIR_PATH="C:/Users/Evaluation/Desktop/EVALUATIONPLATFORM"
    )

    # Create an instance of Microscope
    microscope = CN_X4_500(logger_obj=NodeLogger_obj, camera_index=0)

    # Single image inspection
    microscope.heartbeat()
    x,y = microscope.operate(filename='captured_image', duration_seconds=10, mode_type='real')
    print(y)