import frida
import sys

def on_message(message, data):
    print(message)

session = frida.get_local_device().attach("DummyBank")
script = session.create_script("""
    console.log("Global keys:", Object.keys(globalThis).join(", "));
    console.log("Module functions:", Object.keys(Module).join(", "));
""")
script.on("message", on_message)
script.load()
sys.stdin.read()
