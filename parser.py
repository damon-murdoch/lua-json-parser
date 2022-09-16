# LUA Parser stuff
from luaparser import ast 
from luaparser import astnodes

# JSON Stuff
import json as JSON

# Program Config
import config

# Logging Library
import util.log as log

# OS Libraries
import sys, os

# Given a value from a lua object,
# returns the value depending on the
# type of value provided.
def parse_value(value): 

    try:
        # Value is table
        if isinstance(value, astnodes.Table): 

            # Return the parsed table
            return parse_table(value)

        # Value is name
        if isinstance(value, astnodes.Name): 

            # Return name
            return value.id

        # Value is number
        if isinstance(value, astnodes.Number):

            # Return number
            return value.n

        # Value is string
        elif isinstance(value, astnodes.String):
            
            # Return string
            return value.s

        # Any other type
        else:
            log.write_log(f"Unhandled type: {type(value)}", "warning")

            print(ast.to_pretty_str(value))

    # Failed to process value
    except Exception as e:

        log.write_log(f"{str(e)}", "error")

        # Return null value
        return None

# Given a lua table, loops
# over all of the elements 
# in the table and returns 
# the contents.
def parse_table(table):

    # Table content
    content = {}

    # Loop over all of the fields
    for field in table.fields:

        # Set the key in the content to the value provided
        content[parse_value(field.key)] = parse_value(field.value)

    # Return the table contents
    return content

# Recursively parse the lua object
def parse_object(tree):

    # Default content
    content = {}

    # For each node in the tree
    for node in ast.walk(tree):

        # If the node is a block
        if isinstance(node, astnodes.Block):

            parse_object(node.body)

        # If the node is a name
        if isinstance(node, astnodes.Assign):

            # Loop over all of the targets
            for i in range(len(node.targets)):

                try:

                    # Deref the value, targets
                    value = node.values[i]
                    target = node.targets[i]

                    # Get the value for the index
                    content[target.id] = parse_value(value)

                except Exception as e: # General failure

                    log.write_log(f"{str(e)}", "error")

    # Return the content
    return content

# Parse the lua content
def parse_lua(content):

    # Parse the lua contents
    tree = ast.parse(content)

    # Parse the json content from the tree
    return parse_object(tree)

# Given a filename, returns
# the utf8-encoded content
# from the file.
def get_unicode(filename, access='r'):

    # Return the content from the file, parsed as utf-8
    return open(filename, access, encoding='utf-8').read()

# Given a filename, content and access type writes
# the content provided as utf-8 to the file.
def write_unicode(filename, content, access='w+'):

    # Attempt to open the filename provided
    with open(filename, access, encoding='utf-8') as f:

        # Write the content to the file
        f.write(str(content))

# If this is the main process
if __name__ == '__main__':

    try:

        log.write_log(
            "Starting lua parser ...", 
            "info"
        )

        # Get the arguments for the script
        args = sys.argv[1:]

        # If there is at least one argument
        if len(args) > 0:

            # Loop over the arguments
            for arg in args:

                # List of files to process
                files = []

                # If the path is valid
                if os.path.exists(arg):

                    # If the path is a directory
                    if os.path.isdir(arg):

                        log.write_log(
                            f"Processing directory {arg} ...", 
                            "info"
                        )

                        # Add all of the .lua files to the list
                        for item in os.listdir(arg):

                            # If the file is a .lua file
                            if (item.endswith('.lua')):

                                # Add the file to the list of files to process
                                files.append(os.path.join(arg, item))
                                
                                log.write_log(
                                    f"File found: {item}", 
                                    "info"
                                )

                    else: # Path is file

                        log.write_log(
                            f"File found: {arg}", 
                            "info"
                        )

                        # Add the file to the files list
                        files.append(arg)

                    # Loop over all of the files
                    for item in files:

                        # Get the filename for the file
                        filename = os.path.basename(item)

                        # Strip the file extension from the filename
                        filename_no_ext = os.path.splitext(filename)[0]

                        log.write_log(
                            f"Processing file: {filename} ...", 
                            "info"
                        )

                        # Parse the lua content from the file
                        lua = parse_lua(get_unicode(item))

                        # Attempt to create the output directory
                        outpath = os.path.join(os.getcwd(), config.JSON_OUT)
                        
                        # If the output folder does not exist
                        if not os.path.exists(outpath):

                            # Create the output folder
                            os.mkdir(outpath)

                            log.write_log(
                                f"Output path created: {outpath}", 
                                "info"
                            )

                        # Output filename
                        outfile = f"{filename_no_ext}.json"

                        # Write the json content to the file
                        write_unicode(
                            os.path.join(outpath, outfile), 
                            JSON.dumps(
                                lua, 
                                indent=config.JSON_INDENT, # Indent the json output
                                ensure_ascii=config.JSON_ASCII, # Only use ascii characters
                                sort_keys=config.JSON_SORT # Sort json keys
                            )
                        )

                        log.write_log(
                            f"File saved successfully: {outfile}", 
                            "success"
                        )

                else: # Path is not valid
                    raise Exception(f"Path {arg} does not exist!")

        else: # No arguments
            raise Exception("No lua files provided!")

    except Exception as e: # General failure

        log.write_log(
            f"Script failed: {str(e)}", 
            "error"
        )

        print("usage: parser.py file1.lua [file2.lua] ... [fileN.lua]")