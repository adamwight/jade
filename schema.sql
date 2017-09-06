-- FIXME: Not thrilled about normalizing the wiki and type, but this seemed
-- like an easy way to guarantee data integrity.

-- Reference table pointing to external wiki db.
create table if not exists wiki_ref (
    wiki_id integer unsigned not null primary key auto_increment,

    -- Wiki key, implicit foreign key to sites.site_global_key
    wiki_global_key varchar(32) not null

    -- TODO: How do we get the translated, natural language name?  Or can we
    -- avoid rendering that?
);
create unique index wr_dbname
    on wiki_ref (wiki_global_key);

-- Reference table defining the types of wiki artifact we support.
create table if not exists artifact_type (
    type_id integer unsigned not null primary key auto_increment,

    -- Machine name for this artifact type, e.g. "diff", "revision", "page".
    type_name varchar(64) not null
);
create unique index at_type
    on artifact_type (type_name);

-- Record pointing to an on-wiki artifact being judged.  These are unique, each
-- wiki artifact will have 0..1 records in this table.
create table if not exists artifact (
    -- Automatic primary key.
    artifact_id integer unsigned not null primary key auto_increment,

    -- Wiki where this artifact lives.
    wiki_id integer unsigned not null,

    -- Artifact type
    type_id integer unsigned not null,

    -- Implicit, variable foreign key to the external database, target depends on wiki and type.
    onwiki_id integer unsigned not null
);
create index art_wiki
    on artifact (wiki_id);
create index art_type
    on artifact (type_id);
create unique index art_target
    on artifact (wiki_id, type_id, onwiki_id);
alter table artifact
    add constraint fk_art_wiki foreign key (wiki_id) references wiki_ref (wiki_id)
        on delete restrict on update cascade;

--     add foreign key (type_id) references artifact_type (type_id)
--         on update cascade on delete restrict;

-- Note that the target database and column can vary, so the onwiki foreign key
-- relationship cannot be enforced, (onwiki_id) -> wikidb#tablename.id_column

create table if not exists judgment (
    judgment_id integer unsigned not null primary key auto_increment,

    -- Foreign key to an artifact.
    judgment_artifact_id integer unsigned not null,

    -- Global wiki user ID.
    judgment_user_id integer unsigned not null,

    judgment_created datetime not null,
    judgment_modified datetime not null,

    -- Freeform text 
    judgment_text varbinary(767) not null default '',

    -- A judgment may be promoted or deprecated for various TBD reasons.
    judgment_rank enum ('preferred', 'normal', 'deprecated'),

    -- Bitfield of who can access this judgment.  Zero means public.
    -- Value can only be changed with admin privileges.
    visibility tinyint not null default 0
);
create index ju_artifact
    on judgment (judgment_artifact_id);
create index ju_created
    on judgment (judgment_created);
create index ju_visibility
    on judgment (visibility);
alter table judgment
    add foreign key (judgment_artifact_id) references artifact(artifact_id)
        on update cascade on delete restrict;

create table if not exists scoring_schema (
    schema_id integer unsigned not null primary key auto_increment,
    schema_name varchar(64) not null,
    schema_version varchar(64) not null,
    schema_definition blob not null
);
create index sc_name
    on scoring_schema (schema_name);
create index sc_version
    on scoring_schema (schema_version);
create unique index sc_ref
    on scoring_schema (schema_name, schema_version);

create table if not exists judgment_score (
    judgment_score_id integer unsigned not null primary key auto_increment,

    -- Judgment this score belongs to.
    judgment_id integer unsigned not null,

    -- Schema defining what data this score may contain.
    schema_id integer unsigned not null,

    -- Score data, conforming to the given schema.
    data blob not null,

    created datetime not null,
    -- Note: Scores can only be deprecated, not modified.

    rank enum ('preferred', 'normal', 'deprecated')
);
create index js_judgment
    on judgment_score (judgment_id);
create index js_rank
    on judgment_score (rank);
create index js_schema
    on judgment_score (schema_id);
alter table judgment_score
    add constraint fk_js_judgment foreign key (judgment_id) references judgment(judgment_id)
        on delete cascade on update cascade,

    add constraint fk_js_schema foreign key (schema_id) references scoring_schema(schema_id)
        on delete cascade on update cascade;

-- Each user may only provide one non-deprecated score per schema, per
-- artifact.  This constraint is enforced in code, and newer scores will
-- deprecate older.
