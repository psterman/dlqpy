import os
import json

def generate_image_index():
    image_index = {}
    total_images = 0
    
    # 扫描所有以pic开头的文件夹
    folders = [d for d in os.listdir('.') if d.startswith('pic') and os.path.isdir(d)]
    
    for folder in folders:
        if os.path.exists(folder):
            images = []
            for file in os.listdir(folder):
                if file.lower().endswith(('.jpg', '.png', '.gif', '.jpeg')):
                    images.append(file)
            if images:  # 只添加非空文件夹
                image_index[folder] = images
                total_images += len(images)
    
    # 保存索引和统计信息
    index_data = {
        'folders': image_index,
        'total_images': total_images,
        'last_updated': os.path.getmtime('.')  # 添加更新时间戳
    }
    
    with open('image_index.json', 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"索引生成完成:")
    print(f"- 文件夹数量: {len(folders)}")
    print(f"- 总图片数量: {total_images}")

if __name__ == '__main__':
    generate_image_index() 