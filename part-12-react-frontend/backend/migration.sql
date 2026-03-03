CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> f27082936e23

CREATE TABLE user (
    id INTEGER NOT NULL, 
    first_name VARCHAR(256), 
    surname VARCHAR(256), 
    email VARCHAR NOT NULL, 
    is_superuser BOOLEAN, 
    hashed_password VARCHAR NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_user_email ON user (email);

CREATE INDEX ix_user_id ON user (id);

CREATE TABLE recipe (
    id INTEGER NOT NULL, 
    label VARCHAR(256) NOT NULL, 
    url VARCHAR(256), 
    source VARCHAR(256), 
    submitter_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(submitter_id) REFERENCES user (id)
);

CREATE INDEX ix_recipe_id ON recipe (id);

CREATE INDEX ix_recipe_url ON recipe (url);

INSERT INTO alembic_version (version_num) VALUES ('f27082936e23') RETURNING version_num;

-- Running upgrade f27082936e23 -> fa22a81039dd

UPDATE alembic_version SET version_num='fa22a81039dd' WHERE alembic_version.version_num = 'f27082936e23';

-- Running upgrade fa22a81039dd -> bd31ef3fe973

UPDATE alembic_version SET version_num='bd31ef3fe973' WHERE alembic_version.version_num = 'fa22a81039dd';

