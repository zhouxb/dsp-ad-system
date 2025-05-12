from app import create_app
from app.extensions import db
from app.models.user.user import User, Role, Permission
from app.models.advertiser.advertiser import Advertiser, QualificationFile, Transaction
from app.models.campaign.campaign import Campaign
from app.models.creative.creative import Creative
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random
from sqlalchemy import text

def generate_mock_data():
    app = create_app()
    with app.app_context():
        # 安全地删除所有表
        with db.engine.connect() as conn:
            # 设置数据库字符集
            conn.execute(text("ALTER DATABASE dsp_ad_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            
            # 禁用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # 获取所有表名
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            
            # 删除所有表
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            
            # 启用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # 提交事务
            conn.commit()

        # 创建所有表
        db.create_all()

        # 1. 创建角色
        roles = {
            'admin': Role(
                name='管理员',
                description='系统管理员，拥有所有权限',
                permissions={'permissions': ['*']}
            ),
            'operator': Role(
                name='运营',
                description='运营人员，负责日常运营',
                permissions={'permissions': [
                    Permission.CAMPAIGN_VIEW,
                    Permission.CAMPAIGN_CREATE,
                    Permission.CAMPAIGN_EDIT,
                    Permission.CREATIVE_VIEW,
                    Permission.CREATIVE_CREATE,
                    Permission.CREATIVE_EDIT,
                    Permission.ADVERTISER_VIEW,
                    Permission.REPORT_VIEW
                ]}
            ),
            'advertiser': Role(
                name='广告主',
                description='广告主用户',
                permissions={'permissions': [
                    Permission.CAMPAIGN_VIEW,
                    Permission.CAMPAIGN_CREATE,
                    Permission.CAMPAIGN_EDIT,
                    Permission.CREATIVE_VIEW,
                    Permission.CREATIVE_CREATE,
                    Permission.CREATIVE_EDIT,
                    Permission.REPORT_VIEW
                ]}
            )
        }
        for role in roles.values():
            role.save()

        # 2. 创建管理员和运营用户
        users = {
            'admin': User(
                username='admin',
                email='admin@example.com',
                full_name='系统管理员',
                hashed_password=get_password_hash('admin123'),
                is_active=True,
                is_superuser=True,
                phone='13800138000'
            ),
            'operator': User(
                username='operator',
                email='operator@example.com',
                full_name='运营人员',
                hashed_password=get_password_hash('operator123'),
                is_active=True,
                is_superuser=False,
                phone='13800138001'
            )
        }
        for user in users.values():
            user.save()
            if user.username == 'admin':
                user.roles.append(roles['admin'])
            else:
                user.roles.append(roles['operator'])

        # 3. 创建广告主
        advertisers = []
        for i in range(5):
            advertiser = Advertiser(
                name=f'广告主{i+1}',
                company_name=f'公司{i+1}',
                credit_code=f'91110000{i:08d}',
                contact_person=f'联系人{i+1}',
                contact_phone=f'1380013{8000+i}',
                contact_email=f'advertiser{i+1}@example.com',
                address=f'北京市朝阳区xxx路{i+1}号',
                status='approved',
                balance=10000.0,
                industry='互联网',
                business_type='B2C',
                account_manager_id=users['operator'].id
            )
            advertiser.save()
            advertisers.append(advertiser)

            # 为每个广告主创建用户
            user = User(
                username=f'advertiser{i+1}',
                email=f'advertiser{i+1}@example.com',
                full_name=f'广告主{i+1}用户',
                hashed_password=get_password_hash('advertiser123'),
                is_active=True,
                is_superuser=False,
                phone=f'1380013{8000+i}',
                advertiser_id=advertiser.id
            )
            user.save()
            user.roles.append(roles['advertiser'])

            # 添加资质文件
            for j in range(2):
                file = QualificationFile(
                    advertiser_id=advertiser.id,
                    file_path=f'/uploads/qualifications/{advertiser.id}_{j}.pdf',
                    file_type='pdf',
                    file_size=1024 * 1024,
                    original_name=f'资质文件{j+1}.pdf',
                    status='approved',
                    uploaded_by_id=user.id,
                    reviewed_by_id=users['admin'].id,
                    review_time=datetime.now(),
                    review_comment='审核通过'
                )
                file.save()

            # 添加交易记录
            for j in range(3):
                transaction = Transaction(
                    advertiser_id=advertiser.id,
                    amount=1000.0,
                    balance_after=1000.0 * (j + 1),
                    transaction_type='deposit',
                    reference_id=f'TRX{advertiser.id}_{j}',
                    status='completed',
                    payment_method='bank_transfer',
                    payment_account='6222021234567890123',
                    created_by_id=users['admin'].id,
                    completed_at=datetime.now()
                )
                transaction.save()

        # 4. 创建广告计划
        campaigns = []
        for advertiser in advertisers:
            for i in range(3):
                campaign = Campaign(
                    name=f'广告计划{i+1}',
                    advertiser_id=advertiser.id,
                    status='active',
                    total_budget=10000.0,
                    daily_budget=1000.0,
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=30),
                    bid_strategy='cpc',
                    bid_amount=1.0,
                    targeting={
                        'age_range': [18, 45],
                        'gender': ['male', 'female'],
                        'location': ['北京', '上海', '广州'],
                        'interests': ['科技', '游戏', '购物']
                    }
                )
                campaign.save()
                campaigns.append(campaign)

        # 5. 创建创意
        for campaign in campaigns:
            for i in range(2):
                creative = Creative(
                    name=f'创意{i+1}',
                    advertiser_id=campaign.advertiser_id,
                    campaign_id=campaign.id,
                    status='active',
                    type=random.choice(['image', 'video', 'html5']),
                    format='300x250',
                    file_type='jpg',
                    file_size=1024 * 1024,
                    file_path=f'/uploads/creatives/{campaign.id}_{i}.jpg',
                    title=f'创意标题{i+1}',
                    description=f'创意描述{i+1}',
                    call_to_action='立即购买',
                    landing_url=f'https://example.com/landing/{campaign.id}_{i}',
                    impressions=random.randint(1000, 10000),
                    clicks=random.randint(100, 1000),
                    conversions=random.randint(10, 100),
                    spend=random.uniform(100, 1000)
                )
                creative.save()

        print("Mock data generated successfully!")

if __name__ == '__main__':
    generate_mock_data() 