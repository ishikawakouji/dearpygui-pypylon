import dearpygui.dearpygui as dpg
from pypylon import pylon
from pypylon import genicam
import numpy as np

# Number of images to be grabbed.
countOfImagesToGrab = 100

dpg.create_context()

texture_data = []
for i in range(0, 1024 * 1024):
    # [RGBa] * size
    texture_data.append(1.0)
    texture_data.append(0)
    texture_data.append(0)
    texture_data.append(1.0)

with dpg.texture_registry(show=False):
    dpg.add_dynamic_texture(
        width=1024, height=1024, default_value=texture_data, tag="camera_texture"
    )

with dpg.value_registry():
    dpg.add_string_value(default_value="size: unknown", tag="grab_size")
    dpg.add_string_value(default_value="first pixcel: 0", tag="img00str")


try:
    # init pylon
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()
    cam_name = camera.GetDeviceInfo().GetModelName()

    # get size
    cam_width = camera.Width.GetValue()
    cam_height = camera.Height.GetValue()

    # max buffer size (def.10)
    camera.MaxNumBuffer = 5

    # start grabbing
    # free running
    # camera.StartGrabbingMax(countOfImagesToGrab)
    camera.StartGrabbing()

    with dpg.window(label="dearpygui basler pypylon Window"):
        dpg.add_text("pypylon")
        dpg.add_text("device: " + cam_name)
        dpg.add_text("size: " + str(cam_width) + " x " + str(cam_height))

        dpg.add_text(source="grab_size")
        dpg.add_text(source="img00str")

        dpg.add_image(texture_tag="camera_texture")

    dpg.create_viewport(title="Custom Title", width=1040, height=1040)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # below replaces, start_dearpygui()
    while dpg.is_dearpygui_running():
        # insert here any code you would like to run in the render loop
        # you can manually stop by using stop_dearpygui()

        # grabbing
        if camera.IsGrabbing():
            grabResult = camera.RetrieveResult(
                5000, pylon.TimeoutHandling_ThrowException
            )

            if grabResult.GrabSucceeded():
                grab_flag = True
                grab_w = grabResult.Width
                grab_h = grabResult.Height
                dpg.set_value("grab_size", "size: " + str(grab_w) + " x " + str(grab_w))

                img = grabResult.Array
                img00 = img[0, 0]
                dpg.set_value("img00str", "value: " + str(img00))

                img_flat = np.ravel(img) / 255.0
                next_tex = (
                    np.array([img_flat, img_flat, img_flat, np.ones(grab_w * grab_h)])
                    .ravel("F")
                    .tolist()
                )
                dpg.set_value("camera_texture", next_tex)

            else:
                print("grab err")

            grabResult.Release()

        dpg.render_dearpygui_frame()

    dpg.start_dearpygui()

    camera.Close()
    dpg.destroy_context()

except genicam.GenericException as e:
    # Error handling.
    print("An exception occurred.")
    print(e.GetDescription())
    exitCode = 1
