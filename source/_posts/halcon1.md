---
title: HALCON1笔记1 常用算子
date: 2019-04-07 17:31:39
modified: 
tags: [HALCON]
categories: HALCON
---

入门学习笔记

![示例图片](halcon1/1078211.jpg)
<!--more-->

## draw_rectangle1
用户在窗口画一个矩形。  
鼠标左键按住，指定顶点，画到对角点后松开左键；再次按住左键可以拖动调整；最后点按鼠标右键就确认了这个长方形。
```vbs
dev_open_window(0, 0, 512, 512, 'black', WindowHandle1)  
draw_rectangle1(WindowHandle1, Row1, Column1, Row2, Column2)  
disp_message (WindowHandle1, '顶点：（' + Row1+ ','+ Column1 + '；对角点：（' + Length1 + ',' + Length2 +'）', 'windows', 200, 60, 'blue', 'true')
stop ()
dev_close_window ()
```

## find_text(ocr)
数字字符识别,定位和识别
```vb
dev_update_off ()
dev_close_window ()

read_image (ModelImage, 'cd_cover/cd_cover_01.png')
get_image_size (ModelImage, Width, Height)
dev_open_window (0, 0, Width, Height, 'black', WindowHandle)
set_display_font (WindowHandle, 16, 'mono', 'true', 'false')
dev_set_draw ('margin')
dev_set_line_width (1)
dev_display(ModelImage)

disp_message (WindowHandle, 'Model Image', 'window', 12, 12, 'black', 'true')

disp_continue_message (WindowHandle, 'black', 'true')
stop()

FontName := 'Industrial_0-9_NoRej'
* 
* Create Automatic Text Reader and set some parameters
create_text_model_reader ('auto', FontName, TextModel)
* The printed date has a significantly higher stroke width
* set_text_model_param (TextModel, 'min_stroke_width', 5)
* The "best before" date has a particular and known structure
* set_text_model_param (TextModel, 'text_line_structure', '2 2 2')
* 
* Read the "best before" date


* define the rois

Row1 := 96
Row2 := 149
Column1 := 87
Column2 := 179
gen_rectangle1 (ModelROI, Row1, Column1, Row2, Column2)
area_center (ModelROI, Area, CenterModelROIRow, CenterModelROIColumn)
dev_set_color ('blue')
disp_message (WindowHandle, 'ROI of the model', 'window', 40, 12, 'blue', 'true')
stop ()

*define the roi of the number
gen_rectangle1 (NumberROI, Row2, Column1, Row2 + 30, Column2)
dev_set_color ('magenta')
dev_display (NumberROI)
disp_message (WindowHandle, 'ROI of the numbers', 'window', 60, 12, 'magenta', 'true')
stop ()

* create th model
reduce_domain (ModelImage, ModelROI, ImageReduced)
create_shape_model(ImageReduced, 4, 0, rad(360), 'auto', 'none', 'use_polarity', 30, 10, ModelID)
inspect_shape_model (ImageReduced, ShapeModelImage, ShapeModelRegion, 1, 50)
get_shape_model_contours (ShapeModel, ModelID, 1)


* display the model contours
dev_set_color('blue')
dev_set_line_width (1)
dev_display (ModelImage)
dev_display(ShapeModelRegion)

disp_message (WindowHandle, 'Model image', 'window', 12, 12, 'black', 'true')
disp_message (WindowHandle, 'Shape model', 'window', 40, 12, 'blue', 'true')
disp_continue_message (WindowHandle, 'black', 'true')
stop ()
* Display description
dev_clear_window ()
Message := 'The shape model has been successfully created.'
Message[1] := 'In the next step each image is searched for the'
Message[2] := 'best match of the shape model followed by a'
Message[3] := 'rectification based on the matching results'
Message[4] := 'and the extraction of the numbers.'
Message[5] := ' '
Message[6] := 'The rectification is demonstrated in two'
Message[7] := 'different ways:'
Message[8] := '- rectification of the full search image'
Message[9] := '- rectification of only the ROI of the numbers'
disp_message (WindowHandle, Message, 'window', 12, 12, 'black', 'true')
disp_continue_message (WindowHandle, 'black', 'true')
stop ()

ImageFiles := 'cd_cover/cd_cover_'
for I := 1 to 4 by 1
    dev_set_line_width (1)
    read_image(SearchImage, ImageFiles+I$'.2d')
    find_shape_model(SearchImage, ModelID, 0, rad(360), 0.7, 1, 0.5, 'least_squares', 0, 1, RowMatch, ColumnMatch, AngleMatch, Score)
    
    if (|Score| > 0)
        vector_angle_to_rigid (0, 0,0, RowMatch, ColumnMatch, AngleMatch, MovementOfModel)
        vector_angle_to_rigid (CenterModelROIRow, CenterModelROIColumn, 0, RowMatch, ColumnMatch,AngleMatch, MovementOfObject)
        *
        affine_trans_contour_xld (ShapeModel, ModelAtNewPosition, MovementOfModel)
        affine_trans_region (NumberROI, NumberROIAtNewPosition, MovementOfObject, 'nearest_neighbor')
        *
        dev_display (SearchImage)
        dev_set_color ('blue')
        dev_display (ModelAtNewPosition)
        dev_set_color ('magenta')
        dev_set_line_width (2)
        dev_display (NumberROIAtNewPosition)
        disp_message (WindowHandle, 'Search image ' + I, 'window', 12, 12, 'black', 'true')
        disp_message (WindowHandle, 'Found match', 'window', 40, 12, 'blue', 'true')
        disp_message (WindowHandle, 'ROI of the numbers', 'window', 60, 12, 'magenta', 'true')
        disp_continue_message (WindowHandle, 'black', 'true')
        stop ()
        
        * rectification of the full search image
        hom_mat2d_invert (MovementOfObject, InverseMovementOfObject)
        affine_trans_image (SearchImage, RectifiedSearchImage, InverseMovementOfObject, 'constant', 'false')
    
        * Display the rectified search image and the ROI of the numbers
        dev_clear_window ()
        dev_display (RectifiedSearchImage)
        dev_display (NumberROI)
        disp_message (WindowHandle, '1. Approach: Rectified search image ' + I, 'window', 12, 12, 'black', 'true')
        disp_message (WindowHandle, 'ROI of the numbers', 'window', 40, 12, 'magenta', 'true')
        disp_continue_message (WindowHandle, 'black', 'true')
        stop ()

        * Step 2: Extract the numbers
        * ---------------------------
        * Reduce the domain of the rectified image to the region of the
        * numbers and extract the numbers using a global gray value treshold
        reduce_domain (RectifiedSearchImage, NumberROI, RectifiedNumberROIImage)
        threshold (RectifiedNumberROIImage, Numbers, 0, 128)
        connection (Numbers, IndividualNumbers)
        * 
        * Display the extracted numbers in the reduced rectified image
        dev_set_colored (12)
        dev_set_draw ('fill')
        dev_display (IndividualNumbers)
        disp_message (WindowHandle, 'Extracted numbers', 'window', CenterModelROIRow, Column1 - 50, 'black', 'true')
        stop ()
        
        * Display the original search image (no rectification) and
        * the corresponding ROI of the numbers
        dev_set_draw ('margin')
        dev_set_color ('magenta')
        dev_display (SearchImage)
        dev_display (NumberROIAtNewPosition)
        * 
        * Step 1: Crop the search image
        * -----------------------------
        * Compute the smallest rectangle surrounding the ROI
        * of the numbers parallel to the coordinate axes
        smallest_rectangle1 (NumberROIAtNewPosition, RowRect1, ColumnRect1, RowRect2, ColumnRect2)
        dev_set_color ('lime green')
        disp_rectangle1 (WindowHandle, RowRect1, ColumnRect1, RowRect2, ColumnRect2)
        disp_message (WindowHandle, '2. Approach: Crop search image ' + I, 'window', 12, 12, 'black', 'true')
        disp_message (WindowHandle, 'ROI of the numbers', 'window', 40, 12, 'magenta', 'true')
        * 
        * Crop the image to the determined rectangle around the numbers
        crop_rectangle1 (SearchImage, CroppedSearchImage, RowRect1, ColumnRect1, RowRect2, ColumnRect2)
        * Open a new window displaying the cropped image of the numbers
        Width2 := ColumnRect2 - ColumnRect1 + 1
        Height2 := RowRect2 - RowRect1 + 1
        dev_open_window (0, Width + 10, Width2, Height2, 'black', CroppedWindowHandle)
        dev_set_part (0, 0, Height2 - 1, Width2 - 1)
        dev_display (CroppedSearchImage)
        disp_rectangle1 (CroppedWindowHandle, 0, 0, Height2, Width2)
        * 
        * Display the corresponding message
        Message := 'Cropped image part'
        Message[1] := '(See also the upper right window)'
        disp_message (WindowHandle, Message, 'window', 65, 12, 'lime green', 'true')
        disp_continue_message (WindowHandle, 'black', 'true')
        stop ()
        
         * 
        * Step 2: Rectifiy the cropped search image
        * ------------------------------------------
        * Prepare the transformation matrix needed for the
        * rectification. Add the translation of the cropping to
        * the transformation matrix and then invert the matrix.
        hom_mat2d_translate (MovementOfObject, -RowRect1, -ColumnRect1, MoveAndCrop)
        hom_mat2d_invert (MoveAndCrop, InverseMoveAndCrop)
        * 
        * Rectify the cropped search image using the
        * inverted transformation matrix
        affine_trans_image (CroppedSearchImage, RectifiedROIImage, InverseMoveAndCrop, 'constant', 'true')
        * 
        * Display the rectified cropped search image in a new window
        get_image_size (RectifiedROIImage, Width3, Height3)
        dev_set_part (0, 0, Height3 - 1, Width3 - 1)
        dev_open_window (Height2 + 60, Width + 10, Width3, Height3, 'black', WindowHandle1)
        set_display_font (WindowHandle1, 11, 'mono', 'true', 'false')
        dev_clear_window ()
        dev_display (RectifiedROIImage)
        disp_message (WindowHandle1, 'Rectified cropped image', 'window', 5, 5, 'black', 'true')
        stop ()
        * 
        * Step 3: Extract the numbers
        * ---------------------------
        * Reduce the domain of the rectified and cropped image to the region of
        * the numbers and extract the numbers using a global gray value treshold
        reduce_domain (RectifiedROIImage, NumberROI, RectifiedNumberROIImage)
        threshold (RectifiedNumberROIImage, Numbers, 0, 128)
        connection (Numbers, IndividualNumbers)
        dev_clear_window ()
        dev_display (RectifiedNumberROIImage)
        dev_set_colored (12)
        dev_set_draw ('fill')
        dev_display (IndividualNumbers)
        disp_message (WindowHandle1, 'Extracted numbers', 'window', 5, 5, 'black', 'true')
        stop ()
        
        find_text (RectifiedNumberROIImage, TextModel, TextResultID)
        get_text_object (Characters, TextResultID, 'all_lines')
        get_text_result (TextResultID, 'class', Classes)
        area_center (Characters, Area, Row, Column)
        for Index := 0 to |Classes| - 1 by 1
            disp_message (WindowHandle1, Classes[Index], 'image', Row[Index]-40, Column[Index] - 3, 'green', 'false')
        endfor
        stop ()
    endif
    if (I < 4)
        dev_set_window (CroppedWindowHandle)
        dev_close_window ()
        dev_set_window (WindowHandle1)
        dev_close_window ()
    endif
    
endfor
disp_end_of_program_message (WindowHandle, 'black', 'true')
* 
* Clear the model
clear_shape_model (ModelID)

clear_text_result (TextResultID)
clear_text_model (TextModel)
```
