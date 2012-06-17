#!/bin/bash

VE='/home/timmyt/.virtualenvs/smarttypes'
ST='/home/timmyt/projects/smarttypes/smarttypes/scripts'

source $VE/bin/activate
exec $VE/bin/python $ST/$1 $2

