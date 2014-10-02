#!/usr/bin/python

import os.path
from distutils import dir_util

from glob import glob
from autopkglib import ProcessorError
from autopkglib.DmgMounter import DmgMounter

__all__ = ["Merger"]

class Merger(DmgMounter):
    """Recursively merges everything under source_path with
       destination_path. This is pretty much a copy of 
       Copier, except it uses distutils.dir_util.copy_tree."""
    description = __doc__
    input_variables = {
        "source_path": {
            "required": True,
            "description": (
                "Path to a directory to copy. "
                "Can point to a path inside a .dmg which will be mounted. "
                "This path may also contain basic globbing characters such as "
                "the wildcard '*', but only the first result will be "
                "returned."),
        },
        "destination_path": {
            "required": True,
            "description": "Path to destination.",
        },
    }
    output_variables = {
    }

    __doc__ = description

    def merge(self, source_item, dest_item):
        '''Recursively merges source_item to dest_item.'''
        # merge directories
        try:
            dir_util.copy_tree(source_item, dest_item)
            self.output(
                    "Copied %s to %s" % (source_item, dest_item))
        except BaseException, err:
            raise ProcessorError(
                    "Can't copy %s to %s: %s" % (source_item, dest_item, err))
    
    def main(self):
        source_path = self.env['source_path']
        # Check if we're trying to copy something inside a dmg.
        (dmg_path, dmg, dmg_source_path) = self.parsePathForDMG(source_path)
        try:
            if dmg:
                # Mount dmg and copy path inside.
                mount_point = self.mount(dmg_path)
                source_path = os.path.join(mount_point, dmg_source_path)
            # process path with glob.glob
            matches = glob(source_path)
            if len(matches) == 0:
                raise ProcessorError(
                    "Error processing path '%s' with glob. " % source_path)
            matched_source_path = matches[0]
            if len(matches) > 1:
                self.output(
                    "WARNING: Multiple paths match 'source_path' glob '%s':"
                    % source_path)
                for match in matches:
                    self.output("  - %s" % match)

            if [c for c in '*?[]!' if c in source_path]:
                self.output("Using path '%s' matched from globbed '%s'."
                            % (matched_source_path, source_path))

            # do the copy
            self.merge(matched_source_path, self.env['destination_path'])
        finally:
            if dmg:
                self.unmount(dmg_path)


if __name__ == '__main__':
    PROCESSOR = Merger()
    PROCESSOR.execute_shell()

