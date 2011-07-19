CREATE TABLE category_tbl (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	category VARCHAR(255) NOT NULL,
	count INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE feature_tbl (
	id INTEGER NOT NULL AUTO_INCREMENT,
	feature VARCHAR(255) NOT NULL,
	category VARCHAR(255) NOT NULL,
	count INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX feature_idx ON feature_tbl(feature);
CREATE INDEX category_idx ON category_tbl(category);
