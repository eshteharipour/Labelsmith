from typing import List, Optional

from sqlalchemy import ARRAY, BigInteger, Boolean, DateTime, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class PrismaMigrations(Base):
    __tablename__ = '_prisma_migrations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='_prisma_migrations_pkey'),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    checksum: Mapped[str] = mapped_column(String(64))
    migration_name: Mapped[str] = mapped_column(String(255))
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    applied_steps_count: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    logs: Mapped[Optional[str]] = mapped_column(Text)
    rolled_back_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class AuditLogs(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='audit_logs_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    authorized: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    ipInfo: Mapped[Optional[dict]] = mapped_column(JSONB)
    req: Mapped[Optional[dict]] = mapped_column(JSONB)


class Categories(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='categories_pkey'),
        Index('categories_parent_idx', 'parent')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    parent: Mapped[Optional[int]] = mapped_column(Integer)
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB)
    title: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[str]] = mapped_column(Text)
    media: Mapped[Optional[int]] = mapped_column(Integer)
    title_tokens: Mapped[Optional[str]] = mapped_column(Text)


class City(Base):
    __tablename__ = 'city'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='city_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)

    site: Mapped[List['Site']] = relationship('Site', back_populates='city')


class CrawlerSpecialProducts(Base):
    __tablename__ = 'crawler_special_products'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='crawler_special_products_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    pid: Mapped[int] = mapped_column(BigInteger)
    delay: Mapped[int] = mapped_column(BigInteger)


class Currency(Base):
    __tablename__ = 'currency'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='currency_pkey'),
        Index('currency_name_date_idx', 'name', 'date')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    sources: Mapped[dict] = mapped_column(JSONB)


class Datasheets(Base):
    __tablename__ = 'datasheets'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='datasheets_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    link: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    size: Mapped[int] = mapped_column(BigInteger)
    type: Mapped[str] = mapped_column(Text)
    group: Mapped[str] = mapped_column(Text)
    pdf_pages: Mapped[int] = mapped_column(Integer)
    group_title: Mapped[str] = mapped_column(Text)
    pdf_thumbnail: Mapped[str] = mapped_column(Text)
    disabled: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))

    datasheets_on_reference_products: Mapped[List['DatasheetsOnReferenceProducts']] = relationship('DatasheetsOnReferenceProducts', back_populates='datasheet')


class Donations(Base):
    __tablename__ = 'donations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='donations_pkey'),
        Index('donations_commited_idx', 'commited')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    commited: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    name: Mapped[Optional[str]] = mapped_column(Text)
    mobile: Mapped[Optional[str]] = mapped_column(Text)
    email: Mapped[Optional[str]] = mapped_column(Text)
    amount: Mapped[Optional[int]] = mapped_column(Integer)
    email_md5: Mapped[Optional[str]] = mapped_column(Text)
    authority: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[Optional[str]] = mapped_column(Text)
    date_commited: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))
    ref_id: Mapped[Optional[int]] = mapped_column(BigInteger)


class Files(Base):
    __tablename__ = 'files'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='files_pkey'),
        Index('files_date_idx', 'date')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    size: Mapped[int] = mapped_column(Integer)
    path: Mapped[str] = mapped_column(Text)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    originalname: Mapped[Optional[str]] = mapped_column(Text)
    mimetype: Mapped[Optional[str]] = mapped_column(Text)
    md5sum: Mapped[Optional[str]] = mapped_column(Text)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB)


class IntelRefs(Base):
    __tablename__ = 'intel_refs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='intel_refs_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    partnumber_normalized: Mapped[str] = mapped_column(Text)


class IntelRefsMatches(Base):
    __tablename__ = 'intel_refs_matches'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='intel_refs_matches_pkey'),
        Index('intel_refs_matches_partnumber_idx', 'partnumber'),
        Index('intel_refs_matches_sum_distance_sum_len_diff_idx', 'sum_distance', 'sum_len_diff')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    partnumber: Mapped[str] = mapped_column(Text)
    sum_distance: Mapped[int] = mapped_column(Integer)
    sum_len_diff: Mapped[int] = mapped_column(Integer)
    matched: Mapped[Optional[dict]] = mapped_column(JSONB)


class MgmtCrawlerLogs(Base):
    __tablename__ = 'mgmt_crawler_logs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='mgmt_crawler_logs_pkey'),
        Index('mgmt_crawler_logs_begin_idx', 'begin')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    mgmt_id: Mapped[int] = mapped_column(BigInteger)
    begin: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    update: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))
    status: Mapped[Optional[dict]] = mapped_column(JSONB)
    report: Mapped[Optional[dict]] = mapped_column(JSONB)


class MgmtCrawlerTasks(Base):
    __tablename__ = 'mgmt_crawler_tasks'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='mgmt_crawler_tasks_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    mgmt_id: Mapped[int] = mapped_column(BigInteger)
    begin: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    update: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))
    status: Mapped[Optional[dict]] = mapped_column(JSONB)
    report: Mapped[Optional[dict]] = mapped_column(JSONB)


class NcOutTrackingLogs(Base):
    __tablename__ = 'nc_out_tracking_logs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='nc_out_tracking_logs_pkey'),
        Index('nc_out_tracking_logs_site_id_product_id_idx', 'site_id', 'product_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    site_id: Mapped[Optional[int]] = mapped_column(Integer)
    product_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    product_name: Mapped[Optional[str]] = mapped_column(String(255))


class OpenApiUsers(Base):
    __tablename__ = 'open_api_users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='open_api_users_pkey'),
        Index('open_api_users_username_key', 'username', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(255))
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text('true'))
    search_count: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    name: Mapped[Optional[str]] = mapped_column(String(50))


class RefProductAttributes(Base):
    __tablename__ = 'ref_product_attributes'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='ref_product_attributes_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pid: Mapped[int] = mapped_column(BigInteger)
    key: Mapped[str] = mapped_column(Text)
    value: Mapped[dict] = mapped_column(JSONB)


class ReferenceProducts(Base):
    __tablename__ = 'reference_products'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='reference_products_pkey'),
        Index('reference_products_c_max_price_idx', 'c_max_price'),
        Index('reference_products_c_min_price_c_max_price_idx', 'c_min_price', 'c_max_price'),
        Index('reference_products_c_min_price_idx', 'c_min_price'),
        Index('reference_products_category_idx', 'category'),
        Index('reference_products_name_idx', 'name'),
        Index('reference_products_norm_search_image_key', 'norm_search', 'image', unique=True)
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    media_list: Mapped[dict] = mapped_column(JSONB)
    norm_search: Mapped[str] = mapped_column(Text)
    c_stock: Mapped[int] = mapped_column(Integer)
    c_rels: Mapped[int] = mapped_column(Integer)
    c_sites: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    disabled: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    category: Mapped[Optional[int]] = mapped_column(Integer)
    alternate_name: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text)
    image: Mapped[Optional[int]] = mapped_column(Integer)
    featured_image: Mapped[Optional[int]] = mapped_column(Integer)
    attachments_list: Mapped[Optional[dict]] = mapped_column(JSONB)
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB)
    tags: Mapped[Optional[str]] = mapped_column(Text)
    c_max_price: Mapped[Optional[int]] = mapped_column(Integer)
    c_min_price: Mapped[Optional[int]] = mapped_column(Integer)
    c_ssc_name: Mapped[Optional[str]] = mapped_column(Text)
    shortlink: Mapped[Optional[str]] = mapped_column(Text)
    part_no: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))
    last_compute_date: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))

    datasheets_on_reference_products: Mapped[List['DatasheetsOnReferenceProducts']] = relationship('DatasheetsOnReferenceProducts', back_populates='reference_products')
    refrence_product_history: Mapped[List['RefrenceProductHistory']] = relationship('RefrenceProductHistory', back_populates='reference_products')
    statistic_populate_products: Mapped[List['StatisticPopulateProducts']] = relationship('StatisticPopulateProducts', back_populates='product')
    crawler_products: Mapped[List['CrawlerProducts']] = relationship('CrawlerProducts', back_populates='reference_products')


class Settings(Base):
    __tablename__ = 'settings'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='settings_pkey'),
        Index('settings_type_idx', 'type')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meta_keyword: Mapped[str] = mapped_column(Text)
    meta_desc: Mapped[str] = mapped_column(Text)
    gtag: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(Text)


class StatisticCrawl(Base):
    __tablename__ = 'statistic_crawl'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='statistic_crawl_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    all_products: Mapped[int] = mapped_column(Integer)
    available_products: Mapped[int] = mapped_column(Integer)


class Stats(Base):
    __tablename__ = 'stats'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='stats_pkey'),
        Index('stats_date_idx', 'date')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    dashboard_stats: Mapped[dict] = mapped_column(JSONB)
    dashboard_site_stats: Mapped[dict] = mapped_column(JSONB)


class StatsSummary(Base):
    __tablename__ = 'stats_summary'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='stats_summary_pkey'),
        Index('stats_summary_type_idx', 'type'),
        Index('stats_summary_type_key', 'type', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    type: Mapped[str] = mapped_column(String(55))


class TrackingLogs(Base):
    __tablename__ = 'tracking_logs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tracking_logs_pkey'),
        Index('tracking_logs_type_idx', 'type')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(Text)
    tracking: Mapped[dict] = mapped_column(JSONB)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    date_str: Mapped[str] = mapped_column(Text)
    query: Mapped[Optional[dict]] = mapped_column(JSONB)
    full_url: Mapped[Optional[str]] = mapped_column(Text)
    params: Mapped[Optional[dict]] = mapped_column(JSONB)
    result: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))


class UserRole(Base):
    __tablename__ = 'user_role'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_role_pkey'),
        Index('user_role_sisoog_id_idx', 'sisoog_id'),
        Index('user_role_sisoog_id_key', 'sisoog_id', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sisoog_id: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(Enum('normal_user', 'admin', 'site_manager', name='roles'))


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        Index('users_username_idx', 'username')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text)
    password: Mapped[str] = mapped_column(Text)

    sessions: Mapped[List['Sessions']] = relationship('Sessions', back_populates='users')
    site_info: Mapped[List['SiteInfo']] = relationship('SiteInfo', back_populates='user')


class UsersForms(Base):
    __tablename__ = 'users_forms'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_forms_pkey'),
        Index('users_forms_date_idx', 'date'),
        Index('users_forms_report_type_idx', 'report_type'),
        Index('users_forms_type_idx', 'type')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_type: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(Text)
    full_name: Mapped[Optional[str]] = mapped_column(Text)
    tell: Mapped[Optional[str]] = mapped_column(Text)
    shop_name: Mapped[Optional[str]] = mapped_column(Text)
    date: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))


class DatasheetsOnReferenceProducts(Base):
    __tablename__ = 'datasheets_on_reference_products'
    __table_args__ = (
        ForeignKeyConstraint(['datasheet_id'], ['datasheets.id'], ondelete='RESTRICT', onupdate='CASCADE', name='datasheets_on_reference_products_datasheet_id_fkey'),
        ForeignKeyConstraint(['ref_pid'], ['reference_products.id'], ondelete='RESTRICT', onupdate='CASCADE', name='datasheets_on_reference_products_ref_pid_fkey'),
        PrimaryKeyConstraint('ref_pid', 'datasheet_id', name='datasheets_on_reference_products_pkey')
    )

    ref_pid: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    datasheet_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    disabled: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))

    datasheet: Mapped['Datasheets'] = relationship('Datasheets', back_populates='datasheets_on_reference_products')
    reference_products: Mapped['ReferenceProducts'] = relationship('ReferenceProducts', back_populates='datasheets_on_reference_products')


class RefrenceProductHistory(Base):
    __tablename__ = 'refrence_product_history'
    __table_args__ = (
        ForeignKeyConstraint(['ref_pid'], ['reference_products.id'], ondelete='RESTRICT', onupdate='CASCADE', name='refrence_product_history_ref_pid_fkey'),
        PrimaryKeyConstraint('id', name='refrence_product_history_pkey'),
        Index('refrence_product_history_ref_pid_date_idx', 'ref_pid', 'date')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    count_sites: Mapped[int] = mapped_column(Integer)
    ref_pid: Mapped[int] = mapped_column(BigInteger)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    min_price: Mapped[Optional[int]] = mapped_column(Integer)
    max_price: Mapped[Optional[int]] = mapped_column(Integer)

    reference_products: Mapped['ReferenceProducts'] = relationship('ReferenceProducts', back_populates='refrence_product_history')


class Sessions(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        ForeignKeyConstraint(['uid'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='sessions_uid_fkey'),
        PrimaryKeyConstraint('id', name='sessions_pkey'),
        Index('sessions_sid_idx', 'sid')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    uid: Mapped[int] = mapped_column(Integer)
    sid: Mapped[str] = mapped_column(Text)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    htr: Mapped[Optional[str]] = mapped_column(Text)

    users: Mapped['Users'] = relationship('Users', back_populates='sessions')


class Site(Base):
    __tablename__ = 'site'
    __table_args__ = (
        ForeignKeyConstraint(['city_id'], ['city.id'], ondelete='SET NULL', onupdate='CASCADE', name='site_city_id_fkey'),
        PrimaryKeyConstraint('id', name='site_pkey'),
        Index('site_disabled_idx', 'disabled'),
        Index('site_link_idx', 'link'),
        Index('site_manual_score_idx', 'manual_score'),
        Index('site_spider_id_key', 'spider_id', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(Text)
    disabled: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    link: Mapped[str] = mapped_column(String(100))
    logo: Mapped[Optional[int]] = mapped_column(Integer)
    city_id: Mapped[Optional[int]] = mapped_column(Integer)
    crawler: Mapped[Optional[dict]] = mapped_column(JSONB)
    mgmt_touch: Mapped[Optional[dict]] = mapped_column(JSONB)
    price_is_not_update: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    spider_id: Mapped[Optional[str]] = mapped_column(Text)
    manual_score: Mapped[Optional[int]] = mapped_column(Integer)

    city: Mapped[Optional['City']] = relationship('City', back_populates='site')
    Site_Error: Mapped[List['SiteError']] = relationship('SiteError', back_populates='site')
    crawler_logs: Mapped[List['CrawlerLogs']] = relationship('CrawlerLogs', back_populates='site')
    site_info: Mapped[List['SiteInfo']] = relationship('SiteInfo', back_populates='site')
    spider_log: Mapped[List['SpiderLog']] = relationship('SpiderLog', back_populates='site')
    statistic_site: Mapped[List['StatisticSite']] = relationship('StatisticSite', back_populates='site')
    crawler_products: Mapped[List['CrawlerProducts']] = relationship('CrawlerProducts', back_populates='site')


class StatisticPopulateProducts(Base):
    __tablename__ = 'statistic_populate_products'
    __table_args__ = (
        ForeignKeyConstraint(['product_id'], ['reference_products.id'], ondelete='RESTRICT', onupdate='CASCADE', name='statistic_populate_products_product_id_fkey'),
        PrimaryKeyConstraint('id', name='statistic_populate_products_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(BigInteger)
    count: Mapped[int] = mapped_column(Integer)
    created: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))

    product: Mapped['ReferenceProducts'] = relationship('ReferenceProducts', back_populates='statistic_populate_products')


class SiteError(Base):
    __tablename__ = 'Site_Error'
    __table_args__ = (
        ForeignKeyConstraint(['site_id'], ['site.id'], ondelete='RESTRICT', onupdate='CASCADE', name='Site_Error_site_id_fkey'),
        PrimaryKeyConstraint('id', name='Site_Error_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(Integer)
    checked: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    status: Mapped[str] = mapped_column(Text)
    created: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    errors: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    text_: Mapped[Optional[str]] = mapped_column('text', Text)
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))
    crawl_id: Mapped[Optional[str]] = mapped_column(Text)

    site: Mapped['Site'] = relationship('Site', back_populates='Site_Error')


class CrawlerLogs(Base):
    __tablename__ = 'crawler_logs'
    __table_args__ = (
        ForeignKeyConstraint(['site_id'], ['site.id'], ondelete='RESTRICT', onupdate='CASCADE', name='crawler_logs_site_id_fkey'),
        PrimaryKeyConstraint('id', name='crawler_logs_pkey'),
        Index('crawler_logs_begin_idx', 'begin'),
        Index('crawler_logs_end_idx', 'end'),
        Index('crawler_logs_is_single_product_idx', 'is_single_product'),
        Index('crawler_logs_site_id_begin_idx', 'site_id', 'begin'),
        Index('crawler_logs_site_id_idx', 'site_id'),
        Index('crawler_logs_site_id_is_single_product_idx', 'site_id', 'is_single_product')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    site_id: Mapped[int] = mapped_column(Integer)
    begin: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    task_id: Mapped[str] = mapped_column(Text, server_default=text("''::text"))
    crawl_type: Mapped[str] = mapped_column(Enum('auto', 'manual', name='CrawlType'), server_default=text('\'auto\'::"CrawlType"'))
    end: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))
    status: Mapped[Optional[str]] = mapped_column(Enum('ok', 'crawlab_error', 'other', 'running', name='log_status'))
    all_products: Mapped[Optional[int]] = mapped_column(Integer)
    available_products: Mapped[Optional[int]] = mapped_column(Integer)
    deleted: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    is_single_product: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))

    site: Mapped['Site'] = relationship('Site', back_populates='crawler_logs')
    crawler_products: Mapped[List['CrawlerProducts']] = relationship('CrawlerProducts', back_populates='log')
    price_history: Mapped[List['PriceHistory']] = relationship('PriceHistory', back_populates='log')


class SiteInfo(Base):
    __tablename__ = 'site_info'
    __table_args__ = (
        ForeignKeyConstraint(['site_id'], ['site.id'], ondelete='RESTRICT', onupdate='CASCADE', name='site_info_site_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='site_info_user_id_fkey'),
        PrimaryKeyConstraint('id', name='site_info_pkey'),
        Index('site_info_site_id_idx', 'site_id'),
        Index('site_info_user_id_idx', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    phone: Mapped[str] = mapped_column(Text)
    digital_media_badge: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    e_nemad: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    social_media: Mapped[Optional[dict]] = mapped_column(JSONB)
    e_nemad_data: Mapped[Optional[dict]] = mapped_column(JSONB)

    site: Mapped['Site'] = relationship('Site', back_populates='site_info')
    user: Mapped['Users'] = relationship('Users', back_populates='site_info')


class SpiderLog(Base):
    __tablename__ = 'spider_log'
    __table_args__ = (
        ForeignKeyConstraint(['site_id'], ['site.id'], ondelete='RESTRICT', onupdate='CASCADE', name='spider_log_site_id_fkey'),
        PrimaryKeyConstraint('id', name='spider_log_pkey'),
        Index('spider_log_crawl_id_key', 'crawl_id', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_name: Mapped[str] = mapped_column(Text)
    site_id: Mapped[int] = mapped_column(Integer)
    spider_id: Mapped[str] = mapped_column(Text)
    start: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    crawl_id: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Enum('running', 'finished', 'pending', 'imported', 'error', name='spider_log_status'))
    end: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))
    command: Mapped[Optional[str]] = mapped_column(Text)
    log_file: Mapped[Optional[str]] = mapped_column(Text)

    site: Mapped['Site'] = relationship('Site', back_populates='spider_log')


class StatisticSite(Base):
    __tablename__ = 'statistic_site'
    __table_args__ = (
        ForeignKeyConstraint(['site_id'], ['site.id'], ondelete='RESTRICT', onupdate='CASCADE', name='statistic_site_site_id_fkey'),
        PrimaryKeyConstraint('id', name='statistic_site_pkey'),
        Index('statistic_site_site_id_key', 'site_id', unique=True)
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    site_id: Mapped[int] = mapped_column(Integer)
    all_products: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    available: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    old_product: Mapped[Optional[int]] = mapped_column(Integer)
    categorized: Mapped[Optional[int]] = mapped_column(Integer)

    site: Mapped['Site'] = relationship('Site', back_populates='statistic_site')


class CrawlerProducts(Base):
    __tablename__ = 'crawler_products'
    __table_args__ = (
        ForeignKeyConstraint(['log_id'], ['crawler_logs.id'], ondelete='SET NULL', onupdate='CASCADE', name='crawler_products_log_id_fkey'),
        ForeignKeyConstraint(['ref_pid'], ['reference_products.id'], ondelete='SET NULL', onupdate='CASCADE', name='crawler_products_ref_pid_fkey'),
        ForeignKeyConstraint(['site_id'], ['site.id'], ondelete='RESTRICT', onupdate='CASCADE', name='crawler_products_site_id_fkey'),
        PrimaryKeyConstraint('id', name='crawler_products_pkey'),
        Index('crawler_products_date_idx', 'date'),
        Index('crawler_products_link_name_key', 'link', 'name', unique=True),
        Index('crawler_products_log_id_idx', 'log_id'),
        Index('crawler_products_log_id_site_id_name_price_idx', 'log_id', 'site_id', 'name', 'price'),
        Index('crawler_products_price_idx', 'price'),
        Index('crawler_products_ref_pid_idx', 'ref_pid'),
        Index('crawler_products_ref_pid_price_stock_count_idx', 'ref_pid', 'price', 'stock_count'),
        Index('crawler_products_ref_pid_site_id_idx', 'ref_pid', 'site_id'),
        Index('crawler_products_should_check_images_idx', 'should_check_images'),
        Index('crawler_products_site_id_idx', 'site_id'),
        Index('crawler_products_site_id_name_price_key', 'site_id', 'name', 'price', unique=True),
        Index('crawler_products_stock_count_idx', 'stock_count')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    site_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text)
    norm_search: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer)
    stock_count: Mapped[int] = mapped_column(Integer)
    link: Mapped[str] = mapped_column(String(1024))
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    last_update_price: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    disabled: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    log_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    picture: Mapped[Optional[int]] = mapped_column(Integer)
    picture_link: Mapped[Optional[str]] = mapped_column(String(1024))
    should_check_images: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    category: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)
    ref_pid: Mapped[Optional[int]] = mapped_column(BigInteger)
    inspect: Mapped[Optional[dict]] = mapped_column(JSONB)
    shortlink: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))

    log: Mapped[Optional['CrawlerLogs']] = relationship('CrawlerLogs', back_populates='crawler_products')
    reference_products: Mapped[Optional['ReferenceProducts']] = relationship('ReferenceProducts', back_populates='crawler_products')
    site: Mapped['Site'] = relationship('Site', back_populates='crawler_products')
    price_history: Mapped[List['PriceHistory']] = relationship('PriceHistory', back_populates='crawler_products')


class PriceHistory(Base):
    __tablename__ = 'price_history'
    __table_args__ = (
        ForeignKeyConstraint(['log_id'], ['crawler_logs.id'], ondelete='RESTRICT', onupdate='CASCADE', name='price_history_log_id_fkey'),
        ForeignKeyConstraint(['pid'], ['crawler_products.id'], ondelete='CASCADE', onupdate='CASCADE', name='price_history_pid_fkey'),
        PrimaryKeyConstraint('id', name='price_history_pkey'),
        Index('price_history_pid_date_idx', 'pid', 'date')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    price: Mapped[int] = mapped_column(Integer)
    pid: Mapped[int] = mapped_column(BigInteger)
    log_id: Mapped[int] = mapped_column(BigInteger)

    log: Mapped['CrawlerLogs'] = relationship('CrawlerLogs', back_populates='price_history')
    crawler_products: Mapped['CrawlerProducts'] = relationship('CrawlerProducts', back_populates='price_history')
