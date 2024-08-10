# SublimeMulleObjC

Plugin for Sublime Text to support Objective-C and specifically [mulle-objc](//mulle-objc.github.io/).

Currently this extension highlights Objective-C selectors, and provides a
shortcut to copy the selection into a string, perfect for use in `@selector()`.
Might do more in the future.

Assume you have this in your Sublime Text buffer:

``` objc
- (void) doWithBar:(int) bar andBaz:(int) baz;
```

click on `doWithBar:` or `andBaz:`, then press [SHIFT]-[ALT]-[C] and now you
have the string "doWithBar:andBaz:" in your paste buffer

Add this keyboard shortcut definition to your Sublime Text bindings with the menu
entries "Preferences/Keybindings"

## .sublime-keymap

``` python
[
   {
        "keys": ["alt+shift+c"],
        "command": "copy_objectivec_selector"
   }
]
```

Optionally enable highlighting with the [SHIFT]-[ALT]-[MOUSE-LEFT] and "Preferences/Mouse Bindings":

## .sublime-mousemap

``` python
[
   {
     "button": "button1",  
     "modifiers": ["alt", "shift"],
     "press_command": "drag_select",
     "command": "highlight_objectivec_selector"
   }
]
```

This will clobber one of the predefined mouse actions though.

