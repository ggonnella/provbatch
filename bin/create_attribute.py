#!/usr/bin/env python3

#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

"""
Create a attribute definition record and attribute columns in the
attribute_value tables according to the definition in a given YAML file.

Usage:
  create_attribute.py [options] {db_args_usage} <name> <definition>

Arguments:
{db_args}
  <name>       name of the attribute
  definition:  YAML file containing the attribute definition

Options:
  --testmode       use the parameters for tests
{common}
"""
from schema import And, Or, Use
import yaml
from sqlalchemy import create_engine
import snacli
from attrtables import AttributeValueTables
from provbatch import scripts_helpers,\
                      AttributeDefinitionsManager,\
                      AttributeDefinition

def main(args):
  engine = create_engine(scripts_helpers.database.connection_string_from(args),
                         echo=args["--verbose"],
                         future=True)
  with engine.connect() as connection:
    with connection.begin():
      kwargs = {"target_n_columns": 9} if args["--testmode"] else {}
      avt = AttributeValueTables(connection,
                                 attrdef_class=AttributeDefinition,
                                 tablename_prefix="_".join(\
                                     args["--dbpfx"], "attribute_value_t"),
                                 **kwargs)
      adm = AttributeDefinitionsManager(avt)
      adm.insert(args["<name>"], args["<definition>"])

def validated(args):
  return scripts_helpers.validate(args, scripts_helpers.database.ARGS_SCHEMA,
      {"<name>": And(str, len),
       "<definition>": And(str, Use(open), Use(yaml.safe_load)),
       "--testmode":   Or(None, True, False)})

with snacli.args(scripts_helpers.database.SNAKE_ARGS,
                 input=["<name>", "<definition>"],
                 params=["--testmode", "--verbose"],
                 docvars={"common": scripts_helpers.common.ARGS_DOC,
                          "db_args": scripts_helpers.database.ARGS_DOC,
                          "db_args_usage": scripts_helpers.database.ARGS_USAGE},
                 version="1.0") as args:
  if args: main(validated(args))
