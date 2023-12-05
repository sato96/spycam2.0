CREATE DATABASE `spyCam` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

CREATE TABLE `par_parameters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(100) DEFAULT NULL,
  `code` varchar(20) DEFAULT NULL,
  `value` varchar(100) DEFAULT NULL,
  `fl_deleted` tinyint(1) DEFAULT 0,
  `insert_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `rol_microservices` (
  `id_role` int(11) NOT NULL,
  `id_microservice` int(11) NOT NULL,
  PRIMARY KEY (`id_role`,`id_microservice`),
  KEY `rol_microservices_FK_1` (`id_microservice`),
  CONSTRAINT `rol_microservices_FK` FOREIGN KEY (`id_role`) REFERENCES `rol_roles` (`id`),
  CONSTRAINT `rol_microservices_FK_1` FOREIGN KEY (`id_microservice`) REFERENCES `ws_microservices` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `rol_roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(100) NOT NULL,
  `fl_deleted` int(1) NOT NULL DEFAULT 0,
  `description` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ser_service_areas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(100) DEFAULT NULL,
  `code` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ser_services` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Id incrementale',
  `description` varchar(100) NOT NULL,
  `code` varchar(20) DEFAULT NULL,
  `insert_date` datetime DEFAULT NULL,
  `id_area` int(11) NOT NULL,
  `fl_deleted` tinyint(1) NOT NULL DEFAULT 0,
  `id_url` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ser_services_FK` (`id_url`),
  KEY `ser_services_FK_1` (`id_area`),
  CONSTRAINT `ser_services_FK` FOREIGN KEY (`id_url`) REFERENCES `par_parameters` (`id`),
  CONSTRAINT `ser_services_FK_1` FOREIGN KEY (`id_area`) REFERENCES `ser_service_areas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `usr_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID incrementale',
  `username` varchar(100) NOT NULL,
  `chat_id` varchar(100) DEFAULT NULL COMMENT 'Vari id separati dalla virgola',
  `insert_date` datetime DEFAULT NULL,
  `id_service` int(11) NOT NULL,
  `role` int(11) DEFAULT 2,
  `token` varchar(100) DEFAULT NULL,
  `expiration_date` datetime DEFAULT NULL,
  `fl_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `usr_users_FK` (`id_service`),
  KEY `usr_users_FK_1` (`role`),
  CONSTRAINT `usr_users_FK` FOREIGN KEY (`id_service`) REFERENCES `ser_services` (`id`),
  CONSTRAINT `usr_users_FK_1` FOREIGN KEY (`role`) REFERENCES `rol_roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ws_labels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(100) NOT NULL,
  `description` varchar(150) NOT NULL,
  `fl_deleted` int(1) DEFAULT 0,
  `id_microservice` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ws_labels_FK` (`id_microservice`),
  CONSTRAINT `ws_labels_FK` FOREIGN KEY (`id_microservice`) REFERENCES `ws_microservices` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ws_microservices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(100) NOT NULL,
  `description` varchar(100) NOT NULL,
  `id_service` int(11) DEFAULT NULL,
  `fl_deleted` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `ws_microservices_FK` (`id_service`),
  CONSTRAINT `ws_microservices_FK` FOREIGN KEY (`id_service`) REFERENCES `ser_services` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ws_responses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_microservice` int(11) NOT NULL,
  `text` varchar(150) NOT NULL DEFAULT '',
  `fl_deleted` tinyint(1) NOT NULL DEFAULT 0,
  `error_code` int(11) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  `code` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ws_responses_FK` (`id_microservice`),
  CONSTRAINT `ws_responses_FK` FOREIGN KEY (`id_microservice`) REFERENCES `ws_microservices` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;