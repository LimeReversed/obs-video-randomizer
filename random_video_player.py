import importlib
# obs = __import__("C:/Program Files/obs-studio/data/obs-scripting/64bit/obspython.py")
import obspython as obs
from Helpers import obs_helper
from Helpers import file_helper
from Helpers.list_randomizer import ListRandomizer
import os

current_video_path = ""
video_source_name = ""
initialized = False
directories = [
    r"E:\Projects\Stream\Video\VOD\2024 - Part 1\Clips\Landscape",
    r"E:\Projects\Stream\Video\VOD\2023 - Part 2\Clips\Landscape",
    r"E:\Projects\Stream\Video\VOD\2023 - Part 1\Clips\Landscape",
    r"E:\Projects\Stream\Video\VOD\2022 - Part 2\Clips\Landscape",
    r"E:\Projects\Stream\Video\VOD\2022 - Part 1\Clips\Landscape",
    r"E:\Projects\Stream\Video\VOD\2021 - Part 2\Clips\Landscape",
    r"E:\Projects\Stream\Video\VOD\2021 - Part 1\Clips\Landscape",
    r"E:\Projects\Stream\Video\VOD\2020 - Part 2\Clips\Landscape"
]
video_files = []
list_randomizer: ListRandomizer
list_randomizer_file_path = file_helper.get_script_env_folder_path() + r"\list_randomizer.json"


# OBS script functions
def initialize():
    global video_files
    global video_source_name
    global initialized
    global list_randomizer

    # ATM this method is a call back for a timer in script_load
    obs.remove_current_callback()

    # Initialize video play
    video_files = file_helper.get_files_from_directories(directories)
    list_randomizer = ListRandomizer(video_files)
    json_obj = file_helper.load_json(list_randomizer_file_path)
    print(json_obj["current_last_index"])

    if video_source_name:
        with obs_helper.Source(video_source_name) as video_source:
            if video_source:
                # Events
                obs.obs_frontend_add_event_callback(on_event)
                register_media_ended_signal_handler()

                if obs.obs_source_showing(video_source):
                    play_next_video()

                initialized = True
                print("random_video_player.py initialized")

                properties = obs.obs_source_properties(video_source)
                obs.obs_properties_add_text(properties,
                                               "Folders",
                                               "Add your folders containing videos",
                                               obs.OBS_TEXT_MULTILINE)
                obs.obs_source_update_properties(video_source)
                obs.obs_properties_destroy(properties)


def cleanup():
    global initialized

    if initialized:
        stop_video()
        obs.obs_frontend_remove_event_callback(on_event)
        deregister_media_ended_signal_handler()
        file_helper.save_json(list_randomizer.to_json(), list_randomizer_file_path)
        initialized = False
        print("Cleanup done")


def script_load(settings):
    global video_source_name

    video_source_name = obs.obs_data_get_string(settings, "video_source_name")

    obs.timer_add(initialize, 5000)


def script_unload():
    cleanup()


def script_description():
    return "This script plays all video files in a specified folder in OBS when the source becomes visible."


def script_update(settings):
    global video_source_name

    video_source_name = obs.obs_data_get_string(settings, "video_source_name")


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "video_source_name", "Source Name", obs.OBS_TEXT_DEFAULT)
    return props


# Events
def on_event(event):
    # print(event)
    if event == obs.OBS_FRONTEND_EVENT_SCRIPTING_SHUTDOWN:
        cleanup()


def register_media_ended_signal_handler():
    global video_source_name

    with obs_helper.Source(video_source_name) as source:
        signal_handler = obs.obs_source_get_signal_handler(source)
        obs.signal_handler_connect(signal_handler, "media_ended", media_ended_handler)
        obs.signal_handler_connect(signal_handler, "show", show_handler)
        obs.signal_handler_connect(signal_handler, "hide", hide_handler)


def deregister_media_ended_signal_handler():
    global video_source_name

    with obs_helper.Source(video_source_name) as source:
        signal_handler = obs.obs_source_get_signal_handler(source)
        obs.signal_handler_disconnect(signal_handler, "media_ended", media_ended_handler)
        obs.signal_handler_disconnect(signal_handler, "show", show_handler)
        obs.signal_handler_disconnect(signal_handler, "hide", hide_handler)


def show_handler(call_data):
    play_next_video()


def hide_handler(call_data):
    stop_video()


def media_ended_handler(call_data):
    print("Video ended")
    play_next_video()


# Video control
def play_next_video():
    global current_video_path
    global video_files
    global list_randomizer

    if not video_files:
        print("No video files detected")
        return

    current_video_path = list_randomizer.get_next_element()
    play_video(current_video_path)


def play_video(video_path):
    global video_source_name

    with obs_helper.Source(video_source_name) as video_source:
        media_state = obs.obs_source_media_get_state(video_source)
        if not media_state == obs.OBS_MEDIA_STATE_PLAYING:
            with obs_helper.SourceSettings(video_source) as settings:
                obs.obs_data_set_string(settings, "local_file", video_path)
                obs.obs_source_update(video_source, settings)
                obs.obs_source_media_restart(video_source)
                print("Video started")


def stop_video():
    global video_source_name

    with obs_helper.Source(video_source_name) as video_source:
        media_state = obs.obs_source_media_get_state(video_source)
        if media_state == obs.OBS_MEDIA_STATE_PLAYING:
            obs.obs_source_media_stop(video_source)
            with obs_helper.SourceSettings(video_source) as settings:
                obs.obs_data_set_string(settings, "local_file", "")
                obs.obs_source_update(video_source, settings)
            print("Video stopped")