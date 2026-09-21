class LcdApi:

    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_DISPLAY_CTRL = 0x08
    LCD_CURSOR_SHIFT = 0x10
    LCD_FUNCTION = 0x20
    LCD_CGRAM = 0x40
    LCD_DDRAM = 0x80

    ENTRY_LEFT = 0x02
    ENTRY_SHIFT_DECREMENT = 0x00

    DISPLAY_ON = 0x04
    CURSOR_OFF = 0x00
    BLINK_OFF = 0x00

    FUNCTION_2LINES = 0x08
    FUNCTION_5X8DOTS = 0x00

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns

    def clear(self):
        self.hal_write_command(self.LCD_CLR)

    def move_to(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        self.hal_write_command(
            self.LCD_DDRAM | (col + row_offsets[row])
        )

    def putstr(self, string):
        for char in string:
            self.hal_write_data(ord(char))

    def hal_write_command(self, cmd):
        raise NotImplementedError

    def hal_write_data(self, data):
        raise NotImplementedError