#
# This is for development outside of Sublime Text when
# import sublime doesn't work
#
class Region:
    def __init__(self, begin, end):
        self._begin = begin
        self._end = end

    def begin(self):
        return self._begin

    def end(self):
        return self._end

class Selection:
    def __init__(self):
        self.regions = []

    def add(self, region):
        """Add a region to the selection."""
        self.regions.append(region)

    def clear(self):
        """Clear all regions from the selection."""
        self.regions.clear()

    def prepend(self, region):
        """Prepend a region to the selection."""
        self.regions.insert(0, region)

    def __iter__(self):
        """Make the selection iterable."""
        return iter(self.regions)

    def __len__(self):
        """Return the number of regions."""
        return len(self.regions)

    def __getitem__(self, index):
        """Allow indexing into the selection."""
        return self.regions[index]

# Example usage

class View:
    def __init__(self, lines):
        self.lines = lines
        self._sel  = Selection()

    def sel(self):
        return self._sel

    def rowcol(self, point):
        # Calculate row and column from a point (character index)
        total_chars = 0
        for row, line in enumerate(self.lines):
            if total_chars + len(line) >= point:
                return row, point - total_chars
            total_chars += len(line) + 1  # +1 for the newline character
        return -1, -1  # Return invalid if point is out of range

    def size(self):
        # Calculate the total number of characters, including newlines
        return sum(len(line) for line in self.lines)

    def text_point(self, row, col):
        # Calculate the character position from row and column
        current_pos = 0
        for i in range(row):
            current_pos += len(self.lines[i]) + 1  # +1 for newline character
        return current_pos + col

    def line(self, position):
        # Check if the input is a Region and get the begin position
        if isinstance(position, Region):
            position = position.begin()

        # Convert position to row and column
        row, _ = self.rowcol(position)

        # Calculate the start and end positions of the line
        if 0 <= row < len(self.lines):
            start_pos = self.text_point(row, 0)
            end_pos = start_pos + len(self.lines[row])
            return Region(start_pos, end_pos)

        # Return an invalid region if out of bounds
        return Region(-1, -1)

    def substr(self, region):
        # Return the substring within the given region
        start = region.begin()
        end = region.end()

        start_row, start_col = self.rowcol(start)
        end_row, end_col = self.rowcol(end)

        if start_row == end_row:
            return self.lines[start_row][start_col:end_col]

        # Multi-line region
        substrings = []
        substrings.append(self.lines[start_row][start_col:])
        for row in range(start_row + 1, end_row):
            substrings.append(self.lines[row])
        substrings.append(self.lines[end_row][:end_col])
        return "\n".join(substrings)

    def print_sel( self):
        for region in self._sel:
            s = self.substr(region)
            escaped_string = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
            print( "\"" + escaped_string + "\"")

if __name__ == '__main__':
    # Example usage
    lines = [
        "This is the first line.",
        "This is the second line.",
        "And this is the third line."
    ]

    view   = View(lines)
    region = Region(5, 25)

    print("Region begin:", region.begin())
    print("Region end:", region.end())
    for i in range( 0, 70, 10):
        print("Row and column of point " + str( i) + " " + str( view.rowcol(i)))
        print("Line containing region:", view.line(Region(i, i + 3)))
        print("Substring of region:", view.substr(Region(i, i + 3)))

    # Create a selection
    selection = Selection()

    # Add regions
    selection.add(Region(10, 20))
    selection.add(Region(30, 40))

    # Prepend a region
    selection.prepend(Region(5, 8))

    # Print all regions
    for region in selection:
        print(region)

    # Clear all regions
    selection.clear()
    print("After clearing:", list(selection))
