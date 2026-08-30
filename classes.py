# Each entry: the exact cron schedule string maps to that class's info.
# Edit the "name" fields with your real class names whenever you're ready.

CLASSES = {
    "45 23 * * 0": {  # fires Sunday 6:45 PM CDT -> reminds about Tuesday's class
        "name": "Book Swim Lane for 5:30-6:30pm and Heated Vinyasa for 6:45pm",
        "class_day": "Tuesday",
        "class_time": "6:45 PM",
    },
    "45 22 * * 2": {  # fires Tuesday 5:45 PM CDT -> reminds about Thursday's class
        "name": "Book Swim Lane for 5:15-6:15pm and Molten Mat for 5:45pm",
        "class_day": "Thursday",
        "class_time": "5:45 PM",
    },
    "30 22 * * 3": {  # fires Wednesday 5:30 PM CDT -> reminds about Friday's class
        "name": "Book Heated Vinyasa for 5:30pm",
        "class_day": "Friday",
        "class_time": "5:30 PM",
    },
    "45 15 * * 4": {  # fires Thursday 10:45 AM CDT -> reminds about Saturday's class
        "name": "Book Heated Yoga Sculpt for 10:45am",
        "class_day": "Saturday",
        "class_time": "10:45 AM",
    },
    "0 13 * * 5": {  # fires Friday 8:00 AM CDT -> reminds about Sunday's class
        "name": "Book rooftop Vinyasa Yoga for 8am",
        "class_day": "Sunday",
        "class_time": "8:00 AM",
    },
}
