import qrcode
from PIL import Image

def generate_qrcode(url, output_path='qrcode.png'):
    """
    生成二维码图片
    
    :param url: 要转换的URL地址
    :param output_path: 输出图片路径
    """
    # 创建二维码对象
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # 添加URL数据
    qr.add_data(url)
    qr.make(fit=True)
    
    # 生成二维码图片
    img = qr.make_image(fill_color='#ff6b8a', back_color='white')
    
    # 保存图片
    img.save(output_path)
    print(f"二维码已生成并保存到: {output_path}")
    
    return img

if __name__ == '__main__':
    # 你的网页地址
    website_url = 'https://dadabugaoxin.github.io/dadabugaoxinletter/'
    
    # 生成二维码
    generate_qrcode(website_url, 'qrcode.png')
    
    # 显示生成的二维码
    img = Image.open('qrcode.png')
    img.show()
    print("\n扫码即可访问你的爱心信封网页！")