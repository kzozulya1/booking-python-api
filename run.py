# -*- coding: utf-8 -*-

from code.app import get_app
               
import os 
import logging
from flask import Flask  
                           
application = get_app()   

if __name__ == '__main__':
    application.run(debug=True)