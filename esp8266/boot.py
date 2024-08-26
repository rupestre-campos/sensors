import gc
import main
import machine
try:
    main.main()
except KeyboardInterrupt as e:
    pass
except Exception as e:
    print('Error on boot.py: {}'.format(e))
    gc.collect()
    machine.reset()
    pass
