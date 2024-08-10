# SublimeMulleObjC

This extension highlights Objective-C selectors, and provides a shortcut
to copy the selection into a string, perfect for use in `@selector()`.

Assume you have this in your Sublime Text buffer:

``` objc
- (void) doWithBar:(int) bar andBaz:(int) baz;
```

click on `doWithBar:` or `andBaz:`, then press [SHIFT]-[ALT]-[C] and now you have the string "doWithBar:andBaz:" in your paste buffer


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

## .sublime-keymap

``` python
[
   {
        "keys": ["alt+shift+c"],
        "command": "copy_objectivec_selector"
   }
]
```


