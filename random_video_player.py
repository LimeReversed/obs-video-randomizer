import inspect
import obspython as obs
from Helpers.obs_helper import Source, Data, DataArray
from Helpers import file_helper
from Helpers.list_randomizer import ListRandomizer
import os

current_video_path = ""
video_source_name = ""
initialized = False

list_randomizer: ListRandomizer
# list_randomizer_file_path = (
#    file_helper.get_script_env_folder_path() + r"\list_randomizer.json"
# )


class list_randomizers_item(object):
    def __init__(self):
        self.video_source_name = None
        self.list_randomizer = None


list_randomizers = {"video_list_name": list_randomizers_item}


def get_full_video_list(settings, video_list_name):
    data_array = obs.obs_data_get_array(settings, video_list_name)
    paths = DataArray(data_array).extract_values_from_array_data("str")
    return file_helper.extract_file_list_from_paths(paths)


def get_used_video_list(video_source_name):
    with Source.construct_from_name(video_source_name) as video_source:
        if video_source:
            with Data.construct_source_settings(
                video_source.resource
            ) as video_source_settings:
                if video_source_settings:
                    with DataArray(
                        obs.obs_data_get_array(
                            video_source_settings.resource, "used_videos"
                        )
                    ) as settings_data_array:
                        return settings_data_array.extract_values_from_array_data("str")

    return []


def load_videos(props, prop, settings):
    global list_randomizer

    video_list_name = obs.obs_property_name(prop)
    all_videos = get_full_video_list(settings, video_list_name)
    # Get the video_source_name from the list_randomizers dictionary
    # video_source_name = list_randomizers[video_list_name].video_source_name
    used_videos = get_used_video_list(video_source_name)
    list_randomizers[video_list_name].list_randomizer = (
        ListRandomizer.construct_from_video_list(all_videos, used_videos)
    )


# OBS script functions
def initialize(settings):
    global video_source_name
    global initialized

    print("Initializing")
    # ATM this method is a call back for a timer in script_load
    obs.remove_current_callback()

    # Events
    obs.obs_frontend_add_event_callback(on_event)
    register_media_ended_signal_handler()

    # Videos
    # Loop through the props to  load video for each of them.
    # I can probably get that from list_randomizers
    # I can get source name from that and the have
    # video_list_name be the parameter instead of prop
    load_videos(None, None, settings)

    with Source.construct_from_name(video_source_name) as video_source:
        if video_source:
            if obs.obs_source_showing(video_source.resource):
                play_next_video()

    initialized = True
    print("random_video_player.py initialized")


def cleanup():
    global initialized
    global video_source_name
    global list_randomizer

    if initialized:
        stop_video()
        obs.obs_frontend_remove_event_callback(on_event)
        deregister_media_ended_signal_handler()

        with DataArray.construct_from_list(
            list_randomizer.get_used(), "str"
        ) as used_videos_data_array:
            with Source.construct_from_name(video_source_name) as video_source:
                if video_source:
                    with Data.construct_source_settings(
                        video_source.resource
                    ) as video_source_settings:
                        if video_source_settings:
                            if (
                                obs.obs_data_array_count(
                                    used_videos_data_array.resource
                                )
                                == 0
                            ):
                                return

                            video_source_settings.set_value(
                                "array", "used_videos", used_videos_data_array.resource
                            )
                            obs.obs_source_update(
                                video_source.resource, video_source_settings.resource
                            )

        initialized = False

        print("Cleanup done")


slider_value = 1


def script_load(settings):
    global video_source_name
    global slider_value

    print("Reached Load")
    video_source_name = obs.obs_data_get_string(settings, "video_source_name")
    slider_value = obs.obs_data_get_int(settings, "source_amount")

    def initialize_with_settings():
        initialize(settings)

    obs.timer_add(initialize_with_settings, 3000)


def script_unload():
    cleanup()


def script_description():
    return "This script plays all video files in a specified folder in OBS when the source becomes visible."


def script_update(settings):
    pass


#     global video_source_name
#     global video_files
#
#     video_source_name = obs.obs_data_get_string(settings, "video_source_name")
#
#     print("Script updating")
#     data_array = DataArray(obs.obs_data_get_array(settings, "folder_list"))
#     video_files = obs_helper.extract_paths_from_names(data_array.extract_values_from_array_data("str"))


def callback(props, prop, settings):
    slider_value = obs.obs_data_get_int(settings, obs.obs_property_name(prop))
    initialize_video_source_properties(props, slider_value)
    return True


def initialize_video_source_properties(props, slider_value: int):
    for i in range(0, 5):
        # obs_property_set_visible(obs_property_t * p, bool visible)
        # obs_property_set_enabled(obs_property_t * p, bool enabled)
        obs.obs_properties_remove_by_name(props, f"video_source_name_{i}")
        obs.obs_properties_remove_by_name(props, f"video_list_{i}")

    for i in range(0, slider_value):
        obs.obs_properties_add_text(
            props,
            f"video_source_name_{i}",
            f"Name of video source {i + 1}",
            obs.OBS_TEXT_DEFAULT,
        )
        obs.obs_properties_add_editable_list(
            props,
            f"video_list_{i}",
            f"Videos / Folders for video source {i + 1}",
            obs.OBS_EDITABLE_LIST_TYPE_FILES,
            "*.mp4 *.m4v *.ts *.mov *.mxf *.flv *.mkv *.avi *.mp3 *.ogg *.aac *.wav *.gif *.webm",
            os.path.abspath(os.path.curdir),
        )
        # Add video_list_{i} as key and initialise a list_randomizer_item to that with video_source_name_{i}


def script_properties():
    global slider_value
    props = obs.obs_properties_create()
    slider = obs.obs_properties_add_int(
        props, "source_amount", "Source amount", 1, 5, 1
    )
    obs.obs_property_set_modified_callback(slider, callback)

    initialize_video_source_properties(props, slider_value)

    return props


# Events
def on_event(event):
    # print(event)
    if event == obs.OBS_FRONTEND_EVENT_SCRIPTING_SHUTDOWN:
        cleanup()


def register_media_ended_signal_handler():
    global video_source_name

    # Send in dynamic video source name here, or videolist name?
    with Source.construct_from_name(video_source_name) as source:
        if source:
            signal_handler = obs.obs_source_get_signal_handler(source.resource)
            obs.signal_handler_connect(
                signal_handler, "media_ended", media_ended_handler
            )
            obs.signal_handler_connect(signal_handler, "show", show_handler)
            obs.signal_handler_connect(signal_handler, "hide", hide_handler)


def deregister_media_ended_signal_handler():
    global video_source_name

    with Source.construct_from_name(video_source_name) as source:
        if source:
            signal_handler = obs.obs_source_get_signal_handler(source.resource)
            obs.signal_handler_disconnect(
                signal_handler, "media_ended", media_ended_handler
            )
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
    global list_randomizer

    current_video_path = list_randomizer.get_next_element()

    if current_video_path:
        play_video(current_video_path)


def play_video(video_path):
    global video_source_name

    with Source.construct_from_name(video_source_name) as video_source:
        media_state = obs.obs_source_media_get_state(video_source.resource)
        if not media_state == obs.OBS_MEDIA_STATE_PLAYING:
            with Data.construct_source_settings(video_source.resource) as settings:
                settings.set_value("str", "local_file", video_path)
                obs.obs_source_update(video_source.resource, settings.resource)
                obs.obs_source_media_restart(video_source.resource)
                print("Video started")


def stop_video():
    global video_source_name

    with Source.construct_from_name(video_source_name) as video_source:
        media_state = obs.obs_source_media_get_state(video_source.resource)
        if media_state == obs.OBS_MEDIA_STATE_PLAYING:
            obs.obs_source_media_stop(video_source.resource)
            with Data.construct_source_settings(video_source.resource) as settings:
                settings.set_value("str", "local_file", "")
                obs.obs_source_update(video_source.resource, settings.resource)
            print("Video stopped")


def _inspect_object(obj):
    for name, data in inspect.getmembers(obj):
        if not name.startswith("__"):
            print(f"{name}: {data}")
