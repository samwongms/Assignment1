
import os
import json
import pandas as pd
from datetime import datetime, timedelta
import random
import django
from django.core.files import File
from django.db import IntegrityError, transaction

# Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from doctors.models import Doctor
from listings.models import Listing, Subject
from taggit.models import Tag

# 假设的选项字典（需要根据实际项目调整）
district_choices = {
    'CW': '中西區',
    'WC': '灣仔區',
    'EA': '東區',
    'SO': '南區',
    'KC': '九龍城區',
    'WT': '黃大仙區',
    'KT': '觀塘區',
    'SS': '深水埗區',
    'YT': '油尖旺區',
    'TW': '荃灣區',
    'TM': '屯門區',
    'NS': '北區',
    'ST': '沙田區',
    'SK': '西貢區',
    'IS': '離島區'
}

room_choices = {
    'single': '單人房',
    'double': '雙人房',
    'suite': '套房',
    'shared': '共享房'
}

rooms_choices = {
    '1': '1間',
    '2': '2間',
    '3': '3間',
    '4+': '4間或以上'
}

class EnhancedDataManager:
    def __init__(self):
        self.cleaned_data = {}
        self.generated_emails = set()  # 跟踪已生成的邮箱
        
    def generate_unique_email(self, name, existing_emails=None):
        """生成唯一的邮箱地址"""
        if existing_emails is None:
            existing_emails = set(Doctor.objects.values_list('email', flat=True))
        
        base_name = name.replace(' ', '.').replace('醫生', '').lower()
        domains = ['hospital.com', 'clinic.com', 'medical.com', 'health.com']
        
        for domain in domains:
            email = f"{base_name}@{domain}"
            if email not in existing_emails and email not in self.generated_emails:
                self.generated_emails.add(email)
                return email
        
        # 如果所有组合都存在，添加数字后缀
        for i in range(1, 100):
            for domain in domains:
                email = f"{base_name}{i}@{domain}"
                if email not in existing_emails and email not in self.generated_emails:
                    self.generated_emails.add(email)
                    return email
        
        return f"{base_name}{random.randint(1000,9999)}@medical.com"
    
    def generate_sample_data(self, count_overrides=None):
        """生成样本数据，支持数量覆盖"""
        count_overrides = count_overrides or {}
        
        # 生成 Subject 数据
        subject_names = [
            '心臟科', '神經科', '兒科', '骨科', '皮膚科', 
            '眼科', '牙科', '心理科', '婦產科', '耳鼻喉科',
            '內科', '外科', '精神科', '復健科', '急診科',
            '麻醉科', '放射科', '病理科', '家庭醫學科', '中醫科'
        ]
        
        subjects_count = count_overrides.get('subjects', 10)
        subjects_data = [{'name': name} for name in subject_names[:subjects_count]]
        
        # 获取现有邮箱以避免重复
        existing_emails = set(Doctor.objects.values_list('email', flat=True))
        
        # 生成 Doctor 数据
        doctor_names = [
            '陳大明醫生', '李美麗醫生', '張偉強醫生', '王曉慧醫生', '劉德華醫生',
            '趙敏醫生', '周杰倫醫生', '林志玲醫生', '吳彥祖醫生', '梁朝偉醫生',
            '劉嘉玲醫生', '郭富城醫生', '黎明醫生', '張學友醫生', '楊千嬅醫生',
            '鄭秀文醫生', '古天樂醫生', '謝霆鋒醫生', '容祖兒醫生', '蔡卓妍醫生'
        ]
        
        doctors_count = count_overrides.get('doctors', 6)
        doctors_data = []
        
        for i in range(doctors_count):
            name = doctor_names[i % len(doctor_names)]
            email = self.generate_unique_email(name, existing_emails)
            
            doctor_data = {
                'name': name,
                'description': f'{name}的專業描述，擁有{random.randint(5, 30)}年臨床經驗',
                'phone': f'9{random.randint(1000000, 9999999):07d}',
                'email': email,
                'is_mvp': random.choice([True, False, False])  # 1/3 几率是 MVP
            }
            doctors_data.append(doctor_data)
        
        # 生成 Listing 数据
        listings_templates = [
            {
                'title': '{}專科診所',
                'address_patterns': ['{}皇后大道中{}號', '{}軒尼詩道{}號', '{}彌敦道{}號'],
                'descriptions': [
                    '位於{}核心地帶的專業診所，設備先進，環境舒適',
                    '{}地區的專業醫療中心，提供優質醫療服務',
                    '現代化{}診所，擁有最新醫療設備和專業團隊'
                ]
            },
            {
                'title': '{}醫療中心',
                'address_patterns': ['{}廣東道{}號', '{}青山公路{}號', '{}英皇道{}號'],
                'descriptions': [
                    '綜合性醫療中心，提供多專科醫療服務',
                    '專業醫療團隊，致力於為{}居民提供優質醫療',
                    '設備齊全的醫療中心，環境溫馨舒適'
                ]
            }
        ]
        
        districts = list(district_choices.keys())
        room_types = list(room_choices.keys())
        rooms_options = list(rooms_choices.keys())
        
        listings_count = count_overrides.get('listings', 20)
        listings_data = []
        
        for i in range(listings_count):
            template = random.choice(listings_templates)
            district = random.choice(districts)
            district_name = district_choices[district]
            
            # 从专业科目中随机选择作为诊所特色
            specialty = random.choice(subject_names)
            
            title = template['title'].format(f"{district_name}{specialty}")
            address = random.choice(template['address_patterns']).format(
                district_name, random.randint(1, 999)
            )
            description = random.choice(template['descriptions']).format(district_name)
            
            # 生成相关服务
            services_map = {
                '心臟科': '心電圖,心臟超聲波,24小時心電監測,心血管檢查',
                '神經科': '腦波檢查,神經傳導,肌電圖,頭痛治療',
                '兒科': '疫苗接種,兒童發展評估,過敏測試,生長監測',
                '骨科': '物理治療,骨骼掃描,關節置換,復健治療',
                '皮膚科': '激光治療,皮膚病理,美容注射,過敏測試',
                '眼科': '視力檢查,激光手術,白內障治療,眼底檢查',
                '牙科': '洗牙,補牙,牙齒矯正,植牙手術',
                '心理科': '心理評估,認知治療,壓力管理,心理輔導'
            }
            
            services = services_map.get(specialty, '專業檢查,醫療諮詢,治療服務')
            
            listing_data = {
                'title': title,
                'address': address,
                'district': district,
                'description': description,
                'services': services,
                'service': random.randint(3, 5),
                'room_type': random.choice(room_types),
                'screen': random.randint(1, 5),
                'professional': random.randint(1, 3),
                'rooms': random.choice(rooms_options),
                'is_published': random.choice([True, True, True, False])  # 75% 已发布
            }
            listings_data.append(listing_data)
        
        return {
            'subjects': subjects_data,
            'doctors': doctors_data,
            'listings': listings_data
        }
    
    def clean_data(self, raw_data):
        """清理和验证原始数据"""
        cleaned_data = {}
        
        # 清理 Subject 数据 - 使用 get_or_create 逻辑
        cleaned_subjects = []
        existing_subjects = set(Subject.objects.values_list('name', flat=True))
        
        for subject in raw_data['subjects']:
            cleaned_subject = {
                'name': subject['name'].strip()
            }
            if cleaned_subject['name'] and cleaned_subject['name'] not in existing_subjects:
                cleaned_subjects.append(cleaned_subject)
        
        # 清理 Doctor 数据
        cleaned_doctors = []
        existing_emails = set(Doctor.objects.values_list('email', flat=True))
        
        for doctor in raw_data['doctors']:
            cleaned_doctor = {
                'name': doctor['name'].strip(),
                'description': doctor['description'].strip(),
                'phone': ''.join(filter(str.isdigit, doctor['phone']))[:8],
                'email': doctor['email'].lower().strip(),
                'is_mvp': bool(doctor['is_mvp'])
            }
            # 验证邮箱格式和唯一性
            if ('@' in cleaned_doctor['email'] and 
                '.' in cleaned_doctor['email'] and
                cleaned_doctor['email'] not in existing_emails):
                cleaned_doctors.append(cleaned_doctor)
        
        # 清理 Listing 数据
        cleaned_listings = []
        for listing in raw_data['listings']:
            cleaned_listing = {
                'title': listing['title'].strip()[:200],
                'address': listing['address'].strip()[:200],
                'district': listing['district'].upper(),
                'description': listing['description'].strip(),
                'services': listing['services'],
                'service': max(1, min(5, listing['service'])),
                'room_type': listing['room_type'],
                'screen': max(1, min(5, listing['screen'])),
                'professional': max(1, min(5, listing['professional'])),
                'rooms': listing['rooms'],
                'is_published': bool(listing['is_published'])
            }
            
            # 验证地区选择
            if cleaned_listing['district'] in district_choices:
                cleaned_listings.append(cleaned_listing)
        
        self.cleaned_data = {
            'subjects': cleaned_subjects,
            'doctors': cleaned_doctors,
            'listings': cleaned_listings
        }
        
        return self.cleaned_data
    
    @transaction.atomic
    def save_to_database(self):
        """将清理后的数据保存到Django数据库（使用事务）"""
        created_count = {
            'subjects': 0,
            'doctors': 0,
            'listings': 0
        }
        
        # 保存 Subject
        subject_objects = list(Subject.objects.all())  # 获取现有科目
        for subject_data in self.cleaned_data['subjects']:
            try:
                subject, created = Subject.objects.get_or_create(
                    name=subject_data['name']
                )
                if created:
                    subject_objects.append(subject)
                    created_count['subjects'] += 1
                    print(f"✅ 创建 Subject: {subject.name}")
                else:
                    print(f"⚠️  已存在 Subject: {subject.name}")
            except IntegrityError as e:
                print(f"❌ 创建 Subject 失败: {e}")
        
        # 保存 Doctor
        doctor_objects = list(Doctor.objects.all())  # 获取现有医生
        for doctor_data in self.cleaned_data['doctors']:
            try:
                # 检查是否已存在
                if Doctor.objects.filter(email=doctor_data['email']).exists():
                    print(f"⚠️  已存在 Doctor: {doctor_data['name']} ({doctor_data['email']})")
                    continue
                
                # 创建虚拟图片文件
                photo_path = f'photos/2024/01/doctor_{len(doctor_objects) + 1}.jpg'
                os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                self.create_dummy_image(photo_path)
                
                with open(photo_path, 'rb') as img_file:
                    doctor = Doctor(
                        name=doctor_data['name'],
                        description=doctor_data['description'],
                        phone=doctor_data['phone'],
                        email=doctor_data['email'],
                        is_mvp=doctor_data['is_mvp']
                    )
                    doctor.photo.save(
                        f'doctor_{len(doctor_objects) + 1}.jpg',
                        File(img_file)
                    )
                    doctor.save()
                    doctor_objects.append(doctor)
                    created_count['doctors'] += 1
                
                print(f"✅ 创建 Doctor: {doctor.name} ({doctor.email})")
                
            except IntegrityError as e:
                print(f"❌ 创建 Doctor 失败 {doctor_data['name']}: {e}")
            except Exception as e:
                print(f"❌ 创建 Doctor 时出错 {doctor_data['name']}: {e}")
        
        # 如果没有创建新的医生，使用现有的
        if not doctor_objects:
            doctor_objects = list(Doctor.objects.all())
            print(f"ℹ️  使用现有医生记录: {len(doctor_objects)} 个")
        
        # 保存 Listing
        for i, listing_data in enumerate(self.cleaned_data['listings']):
            try:
                # 分配医生（循环使用）
                doctor = doctor_objects[i % len(doctor_objects)]
                
                # 检查是否已存在类似列表
                existing_listing = Listing.objects.filter(
                    title=listing_data['title'],
                    doctor=doctor
                ).first()
                
                if existing_listing:
                    print(f"⚠️  已存在 Listing: {listing_data['title']}")
                    continue
                
                # 创建虚拟主图片
                main_photo_path = f'photos/2024/01/listing_main_{i + 1}.jpg'
                os.makedirs(os.path.dirname(main_photo_path), exist_ok=True)
                self.create_dummy_image(main_photo_path)
                
                # 创建 Listing 对象
                with open(main_photo_path, 'rb') as main_img:
                    listing = Listing(
                        doctor=doctor,
                        title=listing_data['title'],
                        address=listing_data['address'],
                        district=listing_data['district'],
                        description=listing_data['description'],
                        service=listing_data['service'],
                        room_type=listing_data['room_type'],
                        screen=listing_data['screen'],
                        professional=listing_data['professional'],
                        rooms=listing_data['rooms'],
                        is_published=listing_data['is_published']
                    )
                    listing.photo_main.save(
                        f'listing_main_{i + 1}.jpg',
                        File(main_img)
                    )
                    listing.save()
                
                # 添加服务标签
                services = [s.strip() for s in listing_data['services'].split(',')]
                for service in services:
                    if service:
                        listing.services.add(service)
                
                # 添加专业人员（随机分配2-4个）
                if subject_objects:
                    professionals = random.sample(
                        subject_objects, 
                        min(random.randint(2, 4), len(subject_objects))
                    )
                    listing.professionals.set(professionals)
                
                created_count['listings'] += 1
                print(f"✅ 创建 Listing: {listing.title}")
                
            except Exception as e:
                print(f"❌ 创建 Listing 失败 {listing_data['title']}: {e}")
        
        print(f"\n=== 创建统计 ===")
        print(f"新创建 Subject: {created_count['subjects']}")
        print(f"新创建 Doctor: {created_count['doctors']}")
        print(f"新创建 Listing: {created_count['listings']}")
        
        return created_count
    
    def create_dummy_image(self, filepath):
        """创建虚拟图片文件"""
        try:
            with open(filepath, 'w') as f:
                f.write("dummy image content")
            return True
        except Exception as e:
            print(f"❌ 创建虚拟图片失败 {filepath}: {e}")
            return False
    
    def format_data(self):
        """格式化数据以供显示"""
        # 实现与之前相同...
        pass
    
    def export_to_json(self, filename='django_data_export.json'):
        """导出数据到JSON文件"""
        # 实现与之前相同...
        pass
    
    def import_from_json(self, filename):
        """从JSON文件导入数据"""
        # 实现与之前相同...
        pass
    
    def export_from_database(self, filename='database_export.json'):
        """从数据库导出数据到JSON文件"""
        # 实现与之前相同...
        pass
    
    def display_statistics(self):
        """显示数据统计信息"""
        print("\n=== 数据统计 ===")
        print(f"待创建 Subject 记录: {len(self.cleaned_data.get('subjects', []))}")
        print(f"待创建 Doctor 记录: {len(self.cleaned_data.get('doctors', []))}")
        print(f"待创建 Listing 记录: {len(self.cleaned_data.get('listings', []))}")
        
        # 数据库中的记录数
        print(f"\n=== 数据库当前统计 ===")
        print(f"数据库中的 Subject 记录: {Subject.objects.count()}")
        print(f"数据库中的 Doctor 记录: {Doctor.objects.count()}")
        print(f"数据库中的 Listing 记录: {Listing.objects.count()}")

def main():
    """主函数"""
    manager = EnhancedDataManager()
    
    print("=== Django 数据管理工具 ===")
 
    
    # 询问用户想要创建多少记录
    try:
        listings_count = int(input("\n请输入要创建的 Listing 记录数 (默认 20): ") or "20")
    except ValueError:
        listings_count = 20
    
    count_overrides = {
        'listings': listings_count,
        'doctors': min(10, listings_count // 2),  # 医生数量约为列表的一半
        'subjects': 15  # 固定科目数量
    }
    
    # 1. 生成样本数据
    print(f"\n1. 生成样本数据 ({listings_count} 个 Listing)...")
    raw_data = manager.generate_sample_data(count_overrides)
    
    # 2. 清理数据
    print("\n2. 清理数据...")
    cleaned_data = manager.clean_data(raw_data)
    
    # 3. 显示统计
    manager.display_statistics()
    
    # 4. 保存到数据库
    print("\n3. 保存数据到数据库...")
    try:
        created_count = manager.save_to_database()
        
        if any(created_count.values()):
            print("✅ 数据成功保存到数据库！")
        else:
            print("ℹ️  没有创建新记录（所有数据已存在）")
            
    except Exception as e:
        print(f"❌ 保存到数据库时出错: {e}")
    
    # 5. 最终统计
    print("\n=== 最终数据库统计 ===")
    print(f"Subject 总数: {Subject.objects.count()}")
    print(f"Doctor 总数: {Doctor.objects.count()}")
    print(f"Listing 总数: {Listing.objects.count()}")
    
    print("\n=== 完成 ===")
    print("您可以在Django管理面板中检查数据")

if __name__ == "__main__":
    main()