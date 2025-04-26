-- labels：唱片公司
create table if not exists wikidata_music.labels
(
    label_id   varchar(512)  not null
        primary key,
    label_name varchar(1024) null
);
-- artists：艺术家
create table if not exists wikidata_music.artists
(
    artist_id   varchar(512)  not null
        primary key,
    artist_name varchar(1024) null
);
-- works：作品（歌曲/专辑）
create table if not exists wikidata_music.works
(
    work_id   varchar(512)  not null
        primary key,
    work_name varchar(1024) null
);

-- artist_label：艺术家与唱片公司之间的关系
create table if not exists wikidata_music.artist_label
(
    artist_id varchar(255) not null,
    label_id  varchar(255) not null,
    primary key (artist_id, label_id),
    constraint artist_label_ibfk_1
        foreign key (artist_id) references wikidata_music.artists (artist_id)
            on delete cascade,
    constraint artist_label_ibfk_2
        foreign key (label_id) references wikidata_music.labels (label_id)
            on delete cascade
);

create index label_id
    on wikidata_music.artist_label (label_id);

-- artist_work：艺术家创作作品的关系
create table if not exists wikidata_music.artist_work
(
    artist_id varchar(255) not null,
    work_id   varchar(255) not null,
    primary key (artist_id, work_id),
    constraint artist_work_ibfk_1
        foreign key (artist_id) references wikidata_music.artists (artist_id)
            on delete cascade,
    constraint artist_work_ibfk_2
        foreign key (work_id) references wikidata_music.works (work_id)
            on delete cascade
);

create index work_id
    on wikidata_music.artist_work (work_id);


