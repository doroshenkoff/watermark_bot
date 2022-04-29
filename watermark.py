from PIL import Image, ImageDraw, ImageFont
import io


def create_watermark(img, text):
    # now = datetime.now()
    # name = f'img-{now.year}-{now.month}-{now.day}--{now.hour}-{now.minute}'
    # img_temp = f'static\\{name}.{ext}'

    with Image.open(img) as im:
        width, height = im.size
        x, y = 10, 10
        fillcolor = 'red'
        shadowcolor = 'yellow'

        im_text = Image.new('RGB', (width, height))

        draw = ImageDraw.Draw(im_text)
        font = ImageFont.truetype('arial.ttf', size=width // 20)

        for i in range(0, width, width // 4):
            for j in range(0, height, height // 6):
                # thin border
                draw.text((x + i - 1, y + j), text, font=font, fill=shadowcolor)
                draw.text((x + i + 1, y + j), text, font=font, fill=shadowcolor)
                draw.text((x + i, y + j - 1), text, font=font, fill=shadowcolor)
                draw.text((x + i, y + j + 1), text, font=font, fill=shadowcolor)

                # thicker border
                draw.text((x + i - 2, y + j - 2), text, font=font, fill=shadowcolor)
                draw.text((x + i + 2, y + j - 2), text, font=font, fill=shadowcolor)
                draw.text((x + i - 2, y + j + 2), text, font=font, fill=shadowcolor)
                draw.text((x + i + 2, y + j + 2), text, font=font, fill=shadowcolor)

                # now draw the text over it
                draw.text((x + i, y + j), text, font=font, fill=fillcolor)

        out = Image.blend(im, im_text, 0.08)
    # out.save(img_temp)
    bytes_out = io.BytesIO()
    out.save(bytes_out, format='JPEG')
    return bytes_out.getvalue()
