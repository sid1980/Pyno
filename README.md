# Pyno
**Python-based data-flow visual programming**, what?

![Pyno](screenshots/start.png)

**So, what you can?**
- real-time interactive development
- no predefined nodes - you will code yours 

*(i'm planning some of github-pages-site with nodes to share, so i need your help!)*
- use python as you like (any libs and tips)
- crash-less errors
- perpetuum mobile

*Pyno is an experiment. Real-world scenarios is confusing.*

### How to use

[Check wiki for advanced tutorials!](https://github.com/honix/Pyno/wiki)

**Basics:**

There are only two elements:
- **node** (is a function)
- **field** (is a object, value or lambda function)

Controls:
- Use right-mouse-button to panning
- To spawn node press **N**, to spawn field press **F** on keyboard
- Save and load pyno-file using bottom-right buttons (S-save, L-load)
- Move and select elements by mouse, selected elements can be deleted by **Delete** key
- Selected elements can be **ctrl-c** and **ctrl-v**
- Nodes has a code inside, edit code just by pressing on node and hover code editor
- Last, you want to transfer data from element to element, just press and hold on pin and drop connection to other pin
![Pyno](screenshots/edit.png)

### How to run
To run pyno you must install few libs:

*(type this commands to your command line)*

* ```pip install pyglet```
* ```pip install pyperclip```

Make sure you have Python 3.4 or better on your computer. If true then run ```Pyno.py```

For more efficency i really recommend to use [PyPy implementation](http://pypy.org/)

![Pyno](screenshots/mass_render.png)
