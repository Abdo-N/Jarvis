import os


def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        # STEP 1: Get the absolute path of the working directory.
        # "calculator" (relative) only makes sense depending on where the
        # script is run from. abspath() turns it into a full, unambiguous
        # path from the filesystem root, e.g.
        # "/home/steve/ai-agent-project/calculator"
        absolute_path = os.path.abspath(working_directory)

        # STEP 2: getting full path by joining absolute and directory (relative) paths
        # calling os.path.normpath for safety
        #
        # os.path.join() just glues the two strings together with a "/".
        # os.path.normpath() then resolves any ".." or "." pieces down to
        # what the path *actually* points to. This matters because if
        # `directory` were something sneaky like "../../etc", the joined
        # path would still contain those ".." segments — normpath collapses
        # them so the commonpath check below can't be fooled by an
        # unresolved path.
        target_dir = os.path.normpath(os.path.join(absolute_path, directory))

        # STEP 3: Will be True or False
        # Finds the longest sub-path shared by two paths.
        # For example, if the working directory is "/home/steve/ai-agent-project/calculator"
        # and the target directory is "/home/steve/ai-agent-project/calculator/pkg",
        # then the common path will be "/home/steve/ai-agent-project/calculator".
        # That is, the common path should be the same as the absolute working directory path
        #
        # This is the actual security check. commonpath() finds the longest
        # shared prefix between two paths. If target_dir has escaped outside
        # absolute_path (e.g. via "../"), their shared prefix will be
        # SHORTER than absolute_path itself, so this equality fails and we
        # catch it below.
        valid_target_dir = os.path.commonpath([absolute_path, target_dir]) == absolute_path

        # Cheap, safe, no-filesystem-access check first: reject anything
        # outside the sandbox immediately, before we ever touch the disk.
        # We never want to run os.path.isdir() (or anything else) on a path
        # that hasn't been proven safe yet — that would mean the agent could
        # poke at real files outside its permitted box.
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Only NOW do we touch the filesystem, since we know target_dir is
        # inside the sandbox. isdir() answers a different question than the
        # check above: not "is this allowed?" but "does this actually exist,
        # and is it a directory (not a file)?"
        #
        # This fires in two cases:
        #   1. target_dir doesn't exist at all (e.g. "nonexistent_folder")
        #   2. target_dir exists but is a file, not a folder (e.g. "main.py")
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        # Passed both checks: it's allowed AND it's a real directory.
        return f'Success: "{directory}" is within the working directory'

    except Exception as e:
        # All "tool call" functions must always return a string, never raise.
        # This catches anything unexpected from the os.path calls above and
        # turns it into a string the LLM agent can read instead of crashing.
        return f"Error: {e}"