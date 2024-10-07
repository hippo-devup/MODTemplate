import os

# 设置文本文件和子目录的路径
file_path = 'LSMod.ini'  # 请替换为你的文本文件路径
subdir_path = 'BG'  # 子目录名称

# 计算子目录BG中的文件数量
files = [name for name in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, name)) and name.endswith('.dds')]
file_count = len(files)

# 读取文本文件内容
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# 替换文件中的curr_img数字为新的文件数量
# 使用正则表达式匹配curr_img=后面跟随的数字
import re
pattern = r'global\s*\$n_imgs\s*=\s*\d+'
content = re.sub(pattern, f'global $n_imgs ={file_count}', content)

res = []
re2 = []
for i in range(0, file_count):
	res.append(f'else if $is_load_prev && $curr_img == {i}\n	this = ResourceLS.{i}')
	re2.append(f'[ResourceLS.{i}]\nfilename = .\\BG\\{files[i]}')
	
pattern = r'BEGIN_SCRIPT_GENERATED_SECTION[\s\S]+?endif'
content = re.sub(pattern, f'BEGIN_SCRIPT_GENERATED_SECTION\n' + '\n'.join(res) + '\nendif', content)

pattern = r'BEGIN_RESOURCE[\s\S]+?END_RESOURCE'
content = re.sub(pattern, lambda m: f'BEGIN_RESOURCE\n' + '\n'.join(re2) + '\n;END_RESOURCE', content)

# 将更新后的内容写回文件
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(content)

print(f'文件数量已更新为: {file_count}')
input('按Enter完成')