from pkg_resources import resource_filename, resource_dir
LAMPORT_SCHEDULER_PATH = resource_filename(__name__, "models/lamport_scheduler.mzn")
LAMPORT_ALLOCATOR_PATH = resource_filename(__name__, "models/lamport_allocator.mzn")
INCLUDE_FOLDER_PATH = resource_filename(__name__, "libraries/")