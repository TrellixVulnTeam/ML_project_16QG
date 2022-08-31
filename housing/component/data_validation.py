

from housing.logger import logging
from housing.exception import HousingException
from housing.entity.config_entity import DataValidationConfig
from housing.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
import os,sys
import pandas as pd
import json
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab


class DataValidation:
    
    def __init__(self, data_validation_config:DataValidationConfig,
    data_ingestion_artifact:DataIngestionArtifact):
        try:
            logging.info(f"{'='*20}Data Validation log started.{'='*20} \n\n") 
            
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e :
            raise HousingException(e,sys) from e 
    
    def get_train_and_test_df(self):
        try:
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            return train_df,test_df
        except Exception as e:
            raise HousingException(e,sys) from e
    
    def does_train_test_file_exist(self) -> bool:
        try:
            logging.info("Checking if train and test files are available")
            does_train_file_exist = False
            does_train_file_exist = False
            
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            
            does_train_file_exist = os.path.exists(train_file_path)
            does_test_file_exist = os.path.exists(test_file_path)
            
            are_available = does_train_file_exist and does_test_file_exist
            
            logging.info(f"Train and test files are available: {are_available}")
            
            if not are_available:
                training_file = self.data_ingestion_artifact.train_file_path
                testing_file = self.data_ingestion_artifact.test_file_path
                
                message = f"Training file: {training_file} or Testing file: {testing_file} are not available"
                raise Exception(message)
            
            return are_available
                    
        except Exception as e :
            raise HousingException(e,sys) from e
    
    def validate_dataset_schema(self) -> bool:
        try:
            validation_status = False
            # assignment : validate training and testing dataset using schema file
            #1. number of columns 
            #2. check the value of ocean proximity
            # acceptable values of ocean proximity are: <1H OCEAN, INLAND, NEAR OCEAN, NEAR BAY, ISLAND
            #3. check column names
            
            
            validation_status = True
            return validation_status
        except Exception as e :
            raise HousingException(e,sys) from e
    
    def get_and_save_data_drift_report(self):
        try:
            profile = Profile(sections=[DataDriftProfileSection()])
            train_df,test_df = self.get_train_and_test_df()
            profile.calculate(train_df,test_df)
            report = json.loads(profile.json())         # json.loads converts str output of profile.json() into a pyton object (list/dict)
            
            report_file_path = self.data_validation_config.report_file_path
            report_dir = os.path.dirname(report_file_path)
            os.makedirs(report_dir,exist_ok=True)
            
            with open(self.data_validation_config.report_file_path, "w") as report_file:
                json.dump(report, report_file, indent=6)
            return report
        except Exception as e:
            raise HousingException(e,sys) from e
        
    def save_data_drift_report_page(self):
        try:
            dashboard = Dashboard(tabs=[DataDriftTab()])
            train_df,test_df = self.get_train_and_test_df()
            dashboard.calculate(train_df,test_df)
            
            report_page_file_path = self.data_validation_config.report_page_file_path
            report_page_dir = os.path.dirname(report_page_file_path)
            os.makedirs(report_page_dir,exist_ok=True)
            
            
            dashboard.save(report_page_file_path)   
        except Exception as e:
            raise HousingException(e,sys) from e
    
        
    def is_data_drifting(self) -> bool:
        try:
            report = self.get_and_save_data_drift_report()
            self.save_data_drift_report_page()
            return True
        except Exception as e:
            raise HousingException(e,sys) from e 
    
    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            self.does_train_test_file_exist()
            self.validate_dataset_schema()
            self.is_data_drifting()
            
            data_validation_artifact = DataValidationArtifact(
                schema_file_path=self.data_validation_config.schema_file_path,
                report_file_path=self.data_validation_config.report_file_path,
                report_page_file_path=self.data_validation_config.report_page_file_path,
                is_validated=True,
                message="Data Validation performed successfully"   
            )
            logging.info(f"Data Validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e :
            raise HousingException(e,sys) from e
            
    def __del__(self):
        logging.info(f"{'='*20}Data Validation log completed.{'='*20} \n\n")       