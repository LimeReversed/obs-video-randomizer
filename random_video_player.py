import obspython as obs
from Helpers import obs_helper
from Helpers import file_helper
from Helpers.list_randomizer import ListRandomizer
import os

current_video_path = ""
video_source_name = ""
initialized = False

video_files = []
list_randomizer: ListRandomizer
list_randomizer_file_path = file_helper.get_script_env_folder_path() + r"\list_randomizer.json"


# OBS script functions
def initialize(settings):
    global video_files
    global video_source_name
    global initialized
    global list_randomizer

    # ATM this method is a call back for a timer in script_load
    obs.remove_current_callback()

    data_array = obs.obs_data_get_array(settings, "folder_list")
    video_files = obs_helper.extract_paths_from_names(obs_helper.extract_array_from_array_data(data_array))

    # Initialize video play
    if video_source_name:
        with obs_helper.Source(video_source_name) as video_source:
            if video_source:
                # Events
                obs.obs_frontend_add_event_callback(on_event)
                register_media_ended_signal_handler()

                with obs_helper.SourceSettings(video_source) as video_source_settings:
                    if video_source_settings:
                        print("GOT TO VIDEO SOURCE SETTINGS IN INITIALIZATION")
                        used_videos = obs_helper.extract_array_from_array_data(
                            obs.obs_data_get_array(video_source_settings, "used_videos"))
                        print("used_videos")
                        print(used_videos)

                        list_randomizer = ListRandomizer.construct_from_obs_data(video_files, used_videos)

                initialized = True
                print("random_video_player.py initialized")

                if obs.obs_source_showing(video_source):
                    play_next_video()


def cleanup():
    global initialized
    global video_source_name
    global list_randomizer

    if initialized:
        stop_video()
        obs.obs_frontend_remove_event_callback(on_event)
        deregister_media_ended_signal_handler()
        obs_helper.set_array(video_source_name, list_randomizer.get_used())
        initialized = False

        print("Cleanup done")


def script_load(settings):
    global video_source_name
    global video_files

    video_source_name = obs.obs_data_get_string(settings, "video_source_name")

    def initialize_with_settings():
        initialize(settings)

    obs.timer_add(initialize_with_settings, 3000)


def script_unload():
    cleanup()


def script_description():
    return "This script plays all video files in a specified folder in OBS when the source becomes visible."


def script_update(settings):
    global video_source_name
    global video_files

    video_source_name = obs.obs_data_get_string(settings, "video_source_name")
    data_array = obs.obs_data_get_array(settings, "folder_list")
    video_files = obs_helper.extract_array_from_array_data(data_array)


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "video_source_name", "Source Name", obs.OBS_TEXT_DEFAULT)
    (obs.obs_properties_add_editable_list
     (props, "folder_list", "Add folders",
      obs.OBS_EDITABLE_LIST_TYPE_FILES,
      "*.mp4 *.m4v *.ts *.mov *.mxf *.flv *.mkv *.avi *.mp3 *.ogg *.aac *.wav *.gif *.webm",
      os.path.abspath(os.path.curdir)))

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
