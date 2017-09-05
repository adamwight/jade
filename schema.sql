-- FIXME: Not thrilled about normalizing the wiki and type, but it seems like
-- the best way to ensure data integrity.

-- Reference table pointing to external wiki db.
create table if not exists wiki (
    wiki_id integer unsigned not null auto_increment,
    -- Wiki database name
    wiki_dbname varchar(32) not null,
    -- TODO: How do we get the translated, natural language name?  Can we avoid
    -- needing that?

    primary key (wiki_id),
    unique key (wiki_dbname)
);

-- Reference table defining the types of wiki artifact we support.
create table if not exists artifact_type (
    type_id integer unsigned not null auto_increment,
    type_name varchar(64) not null,

    primary key (type_id),
    unique key (type_name)
);

-- Unique record pointing to an on-wiki artifact being judged.
create table if not exists artifact (
    -- Automatic primary key.
    artifact_id integer unsigned not null auto_increment,
    -- Wiki where this artifact lives.
    wiki_id integer unsigned not null,
    -- Artifact type
    type_id integer unsigned not null,
    -- Implicit, variable foreign key to the external database, target depends on wiki and type.
    onwiki_id integer unsigned not null,

    primary key (artifact_id),
    index (wiki_id),
    index (type_id),
    unique key (wiki_id, type_id, onwiki_id),
    foreign key (wiki_id) references wiki(wiki_id),
    foreign key (type_id) references artifact_type(type_id)
);

create table if not exists judgment (
    judgment_id integer unsigned not null auto_increment,
    judgment_artifact_id integer unsigned not null,
    judgment_created datetime not null,
    judgment_comment blob,
    visibility tinyint not null default 0,

    primary key (judgment_id),
    index (judgment_created)
);

create table if not exists scoring_schema (
    schema_id integer unsigned not null auto_increment,
    schema_name varchar(64) not null,
    schema_version varchar(64) not null,
    schema_definition blob not null,

    primary key (schema_id),
    index (schema_name),
    index (schema_version),
    unique key (schema_name, schema_version)
);

create table if not exists judgment_score (
    judgment_score_id integer unsigned not null auto_increment,
    -- Judgment this score belongs to.
    judgment_id integer unsigned not null,
    -- Schema defining what data this score may contain.
    schema_id integer unsigned not null,
    -- Score data, conforming to the given schema.
    data blob not null,
    created datetime not null,
    rank enum ('preferred', 'normal', 'deprecated'),

    primary key (judgment_score_id),
    index (judgment_id),
    index (rank),
    foreign key (judgment_id) references judgment(judgment_id),
    foreign key (schema_id) references scoring_schema(schema_id)
);
