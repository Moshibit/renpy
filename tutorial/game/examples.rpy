# This file is responsible for displaying code examples. It expects to see
# comments like #begin foo and #end foo a the start of lines. The code is
# then used to create example fragments.
#
# When we see:
#
# show example foo bar
#
# We concatenate fragements foo and bar, higlight them, wrap them into a
# viewport, button and transform, and display them to the user.

transform example_transform:
    ypos 450 yanchor 1.0 xpos 0 xanchor 0

    on replace:
        crop (0, 0, 800, 120)
            
    on show:
        crop (0, 0, 800, 0)
        linear .5 crop (0, 0, 800, 120)

    on hide:
        linear .5 crop (0, 0, 800, 0)

init python:

    import re
    
    KEYWORDS = """\
                and
                as
                assert
                break
                class
                continue
                def
                elif
                else
                except
                exec
                finally
                for
                from
                global
                if
                import
                in
                is
                lambda
                not
                or
                pass
                print
                raise
                return
                try
                while
                with
                yield

                at
                behind
                call
                expression
                hide
                image
                init
                jump
                label
                menu
                onlayer
                python
                scene
                set
                show
                play
                queue
                stop
                sound
                music
                fadeout
                fadein
                loop
                noloop
                if_changed
                voice
                sustain
                nvl
                clear
                window
                pause
                define
                transform
                """

    KEYWORDS = [ i.strip() for i in KEYWORDS.split() ]
    KWREGEX = r"|".join(KEYWORDS)

    regex = r"(?P<keyword>\b(" + KWREGEX + r")\b)|(?P<string>\"([^\"]|\\.)*\")|(?P<comment>#.*)"
    regex = re.compile(regex)
    
    # This maps from example name to the text of the fragment.    
    examples = { }

    class __Example(object):
        """
         When parameterized, this displays an example window, containing
         example text from blocks with those parameters.
         """

        def colorize(self, m):
            if m.group("string"):
                return "{color=#060}" + m.group(0) + "{/color}"

            if m.group("keyword"):
                return "{color=#840}" + m.group(0) + "{/color}"

            if m.group("comment"):
                return "{color=#600}" + m.group(0) + "{/color}"
                
            
            
            
            return m.group(0)
                        

        
        def parameterize(self, name, args):

            # Collect the examples we use.            
            lines1 = [ ]
            
            for i in args:
                if i not in examples:
                    raise Exception("Unknown example %r." % i)
                lines1.extend(examples[i])


            # Strip off doubled blank lines.
            last_blank = False
            lines = [ ]
            
            for i in lines1:

                if not i and last_blank:
                    continue

                last_blank = not i

                i = regex.sub(self.colorize, i)
                
                lines.append(i)
            
            # Join them into a single string.
            code = "\n".join(lines)

            ct = Text(code, size=16, color="#000")
            vp = Viewport(ct, child_size=(2000, 2000), ymaximum=120, draggable=True, mousewheel=True)
            w = Window(vp, background = "#fffc", right_padding=0, bottom_padding=0, yminimum=0)
            return example_transform(w)

image example = __Example()
        
                
init python hide:

    import os.path
    import re
    
    # A list of files we will be scanning.
    files = [ ]
    
    for i in os.listdir(config.gamedir):
        if i.endswith(".rpy"):
            files.append(os.path.join(config.gamedir, i))

    for fn in files:

        f = file(fn, "r")

        open_examples = set()
        
        for l in f:

            l = l.rstrip()
            
            m = re.match("\s*#begin (\w+)", l)
            if m:
                example = m.group(1)

                if example in examples:
                    raise Exception("Example %r is defined in two places.", example)

                open_examples.add(example)
                examples[example] = [ ]

                continue

            m = re.match("\s*#end (\w+)", l)
            if m:
                example = m.group(1)

                if example not in open_examples:
                    raise Exception("Example %r is not open.", example)

                open_examples.remove(example)
                continue

            for i in open_examples:
                examples[i].append(l)

        if open_examples:
            raise Exception("Examples %r remain open at the end of %r" % (open_examples, fn))

        f.close()
            
