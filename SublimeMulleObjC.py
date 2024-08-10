import sublime
import sublime_plugin
import re


class ObjectiveCSelectorParser:
    def reset(self):
        self.stack = []
        self.in_single_quote = False
        self.in_double_quote = False

    def __init__(self):
        self.reset()

    def get_opening_character(self, opening_char):
     # Mapping of opening to closing characters
        matching_pairs = {
            '>': '>',
            ')': '(',
            ']': '[',
            '}': '{'
        }

        # Return the corresponding closing character
        return matching_pairs.get(opening_char, None)

    def get_closing_character(self, closing_char):
     # Mapping of opening to closing characters
        matching_pairs = {
            '<': '>',
            '(': ')',
            '[': ']',
            '{': '}'
        }

        # Return the corresponding closing character
        return matching_pairs.get(closing_char, None)

    def find_previous_colon_index(self, s):
        escape = False
        # Iterate backwards through the string
        for i in range(len(s) - 1, -1, -1):
            if escape:
                escape = False
                continue

            if (self.in_single_quote or self.in_double_quote) and i >0 :
                prev_char = s[i - 1]
                if prev_char == '\\':
                    escape = True
                    continue

            char = s[i]
            if char == '"':
                if not self.in_single_quote:
                    self.in_double_quote = not self.in_double_quote
                continue

            if char == "'":
                if not self.in_double_quote:
                    self.in_single_quote = not self.in_single_quote
                continue

            if self.in_single_quote or self.in_double_quote:
                continue

            if char == ':':
                return i

            if char in '({[<':
                # If a opening bracket is found, check if it matches the last closing bracket
                other = self.get_closing_character( char)
                if not self.stack or self.stack[-1] != other:
                    return -2
                self.stack.pop()
                continue

            if char in ')]]>':
                self.stack.append( char)
                continue

        return -1

    def find_next_colon_index(self, s):
        escape = False
        for i in range(len(s)):
            if escape:
                escape = False
                continue

            char = s[i]
            if (self.in_single_quote or self.in_double_quote) and char == '\\':
                escape = True
                continue

            if char == '"':
                if not self.in_single_quote:
                    self.in_double_quote = not self.in_double_quote
                continue

            if char == "'":
                if not self.in_double_quote:
                    self.in_single_quote = not self.in_single_quote
                continue

            if self.in_single_quote or self.in_double_quote:
                continue

            if char == ':':
                return i

            if char in ')]]>':
                # If a closing bracket is found, check if it matches the last opening bracket
                other = self.get_opening_character( char)
                if not self.stack or self.stack[-1] != other:
                    return -2
                self.stack.pop()
                continue

            if char in '({[<':
                self.stack.append( char)
                continue

        return -1
    def looks_like_start(self, s):
        stripped_string = s.lstrip()

        # Check if the first character is one of the specified characters
        if stripped_string and stripped_string[0] in '-+[@':
            return True
        return False

    def looks_like_end( self, s):
        # Strip leading and trailing whitespace
        stripped_string = s.strip()

        # Check if the string is empty
        if not stripped_string:
            return True

        # Check for single-line comment starting with //
        if stripped_string.startswith('//'):
            return True

        # Check for block comment starting and ending with /* */
        if stripped_string.startswith('/*'):
            return True

        # Check if the string ends with a semicolon
        if stripped_string.endswith(';'):
            return True

        return False

    def expand_identifier(self, line_content, cursor_pos):
        # Regular expression to match Objective-C selector fragment
        pattern = re.compile(r'\b(\w+:?)\s*(\(.+?\))?')
        matches = pattern.finditer(line_content)

        for match in matches:
            start, end = match.span(1)
            if start <= cursor_pos <= end:
                return match
        return False

# SublimeText3 can't deal with ..eCSelector... for the command string
class HighlightObjectivecSelectorCommand(sublime_plugin.TextCommand):
    def current_line_region(self, view, position):
        # Get the current cursor position
        line_num    = view.rowcol(position)[0]
        line_region = view.line(view.text_point(line_num, 0))
        return line_region
    def previous_line_region(self, view, position):
        # Get the current cursor position
        line_num = view.rowcol(position)[0] -1
        if( line_num < 0):
            return sublime.Region( -1, -1)

        line_region = view.line(view.text_point(line_num, 0))
        return line_region

    def next_line_region(self, view, position):
        # Get the current cursor position
        line_num = view.rowcol(position)[0] + 1
        total_lines = self.view.rowcol(self.view.size())[0] + 1

        # Check if the next line exists
        if line_num >= total_lines:
            return sublime.Region( -1, -1)

        line_region = view.line(view.text_point(line_num, 0))
        return line_region

    def prefix_region(self, view, region):
        line_num       = view.rowcol(region.begin())[0]
        line_region    = view.line( view.text_point( line_num, 0))
        prefix_region  = sublime.Region( line_region.begin(), region.begin())  # 100
        return prefix_region

    def suffix_region(self, view, region):
        line_num       = view.rowcol(region.begin())[0]
        line_region    = view.line( view.text_point( line_num, 0))
        suffix_region  = sublime.Region( region.end(), line_region.end())  # 100
        return suffix_region

    def trace_back(self, view, parser, region, is_new, new_sels):
        #
        # Get the string of the current line region that precedes the
        # cursor selector bit (already in new_sels)
        #
        if is_new:
            region = self.current_line_region(view, region.begin())
        else:
            region = self.prefix_region( view, region)
        line_content = view.substr(region)
        if not line_content:
            return

        # check if we find another bit (e.g. "foo:(int) a bar:" we are at bar: and we want to
        # get foo:
        index = parser.find_previous_colon_index( line_content)
        # broken content, abort
        if index == -2:
            return

        # if we were searching a "new" previous line and found nothing then bail
        if index == -1 and is_new:
            return

        # found a colon, lets grab it and then get back
        # gotta match though or ?
        if index != -1:
            match = parser.expand_identifier( line_content, index)
            if not match:
                return

            start, end = match.span(1)
            line_region = sublime.Region( start + region.begin(),
                                          end  + region.begin())
            new_sels.append(line_region)

            # just continue with current line like before
            self.trace_back( view, parser, line_region, False, new_sels)
            return

        # if our line looks like the start of something then we are done
        line_region  = self.current_line_region( view, region.begin())
        line_content = view.substr(line_region)
        if parser.looks_like_start(line_content):
            return

        #
        # look for next fragment in previous line
        #
        line_region  = self.previous_line_region( view, line_region.begin())
        line_content = view.substr(line_region)

        if parser.looks_like_end(line_content):
            return

        self.trace_back( view, parser, sublime.Region( line_region.end() -1, line_region.end()), True, new_sels)
        return


    def trace_forward(self, view, parser, region, is_new, new_sels):
        #
        # Get the string of the current line region that precedes the
        # cursor selector bit (already in new_sels)
        #
        if is_new:
            region = self.current_line_region(view, region.begin())
        else:
            region = self.suffix_region( view, region)

        line_content = view.substr( region)
        if not line_content:
            return

        # check if we find another bit (e.g. "foo:(int) a bar:" we are at bar: and we want to
        # get foo:
        index = parser.find_next_colon_index( line_content)
        # broken content, abort
        if index == -2:
            return

        # if we were searching a "new" previous line and found nothing then bail
        if index == -1 and is_new:
            return

        # found a colon, lets grab it and then get back
        # gotta match though or ?
        if index != -1:
            match = parser.expand_identifier( line_content, index)
            if not match:
                return

            start, end = match.span(1)
            line_region = sublime.Region( start + region.begin(),
                                          end  + region.begin())
            new_sels.append(line_region)

            # just continue with current line like before
            self.trace_forward( view, parser, line_region, False, new_sels)
            return

        # if our line looks like the end of something then we are done
        line_region  = self.current_line_region( view, region.begin())
        line_content = view.substr(line_region)
        if parser.looks_like_end(line_content):
            return

        #
        # look for next fragment in previous line
        #
        line_region  = self.next_line_region( view, line_region.begin())
        line_content = view.substr(line_region)

        if parser.looks_like_start(line_content):
            return

        self.trace_forward( view,  parser,sublime.Region( line_region.begin(), line_region.begin() + 1), True, new_sels)
        return


    def run(self, edit):
        view = self.view
        sels = view.sel()
        new_sels = []

        if len(sels) < 1:
            return

        # Get the current cursor position
        cursor_pos   = sels[0].begin()
        line_region  = view.line(cursor_pos)
        line_content = view.substr(line_region)

        # Find the identifier under the cursor
        parser   = ObjectiveCSelectorParser()
        index    = cursor_pos - line_region.begin()
        match    = parser.expand_identifier( line_content, index)
        if not match:
            return

        start, end = match.span(1)
        region = sublime.Region( start + line_region.begin(),
                                 end  + line_region.begin())
        new_sels.append(region)

        identifier = match.group(1)
        if identifier.endswith(':'):
           self.trace_back( view, parser, region, False, new_sels)
           parser.reset()
           self.trace_forward( view, parser, region, False, new_sels)

        sels.clear()
        for new_sel in new_sels:
            sels.add(new_sel)

class CopyObjectivecSelectorCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        view.run_command("highlight_objectivec_selector")

        sels = view.sel()
        combined_string = ""

        # Concatenate all selected text fragments, removing whitespace
        for sel in sels:
            combined_string += view.substr(sel).strip()

        if combined_string:
            sublime.set_clipboard(combined_string)


if __name__ == '__main__':

    lines = [
        "junk",
        "- (void) foo:(int) a",
        "         bar:(int) c",
        "         baz:(int) d",
        "junk"
    ]

    view = sublime.View(lines)
    view.sel().clear()
    view.sel().add( sublime.Region( 35, 36))
    view.print_sel()

    highlighter = HighlightObjectivecSelectorCommand( view)
    highlighter.run( True)
    print( "1.1: ---------------------------------------")

    view.sel().clear()
    view.sel().add( sublime.Region( 17, 32))
    view.print_sel()

    highlighter = HighlightObjectivecSelectorCommand( view)
    highlighter.run( True)
    print( "1.2: ---------------------------------------")

    # Example usage
    lines = [
        "junk",
        "- (void) foo:(int) a bar:(int) c;",
        "junk"
    ]

    view = sublime.View(lines)
    view.sel().clear()
    view.sel().add( sublime.Region( 27, 28))
    view.print_sel()

    highlighter = HighlightObjectivecSelectorCommand( view)
    highlighter.run( True)
    print( "2.1: ---------------------------------------")

    view.sel().clear()
    view.sel().add( sublime.Region( 15, 16))
    view.print_sel()

    highlighter = HighlightObjectivecSelectorCommand( view)
    highlighter.run( True)
    print( "2.2: ---------------------------------------")

    view.sel().clear()
    view.sel().add( sublime.Region( 3, 4))
    view.print_sel()

    highlighter = HighlightObjectivecSelectorCommand( view)
    highlighter.run( True)
    print( "2.3: ---------------------------------------")
