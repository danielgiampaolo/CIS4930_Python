=======
NetView
=======

NetView is a simple Django app.

Detailed documentation is in...

Quick start
-----------

1. Clone Repository:: 
    
    https://github.com/danielgiampaolo/CIS4930_Python.git

2. Update PIP::

    python3 -m pip install --upgrade pip

3. Configure Virtual Environment (modify at will)::

    python3 -m venv netview_env
    source netview_env/bin/activate (activate virtual env)
    pip install Django==3.0.7
    cd src
    python manage.py migrate

4. Install Dependencies (taken care off with pip install NetView)::
    
    pip install matplotlib
    pip install networkx

5. Run Server (from within ./src/):: 

    python manage.py runserver
    http://127.0.0.1:8000/ (default)
