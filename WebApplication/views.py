import paho.mqtt.client as mqtt
import sqlite3

from _testcapi import awaitType
from flask import Flask, render_template, request, flash, redirect


def test(id):
    return int(id)
