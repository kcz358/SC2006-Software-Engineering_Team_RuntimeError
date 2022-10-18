--
-- Table structure for table `article`
--

DROP TABLE IF EXISTS `article`;

CREATE TABLE `article` (
  `id` tinyint(4) DEFAULT NULL,
  `author` varchar(11) DEFAULT NULL,
  `date` varchar(17) DEFAULT NULL,
  `caption` varchar(35) DEFAULT NULL,
  `genre` varchar(11) DEFAULT NULL,
  `body` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Dumping data for table `article`
--

LOCK TABLES `article` WRITE;
/*!40000 ALTER TABLE `article` DISABLE KEYS */;
INSERT INTO `article` VALUES (1,'John Tan','11 February 2019','How do you know what to recycle?','EDUCATIONAL','Firstly, use a bag to store all your recyclables. No requirement to sort the recyclables as they will  be sorted after collection. ,\r\n\r\nSecondly, know what can or cannot be recycled.\r\nOn the blue bin, there are labels as to which items can be recycled. Recyling the incorrect items can cause environmental issues and cause a hindrance to the staff.\r\n\r\nThirdly, make sure your items are not contaiminated with food or liquids.\r\nThis causes baterial growth which degrades the condition of the product.'),(2,'Sally Lee','10 September 2020','Why thrift?','EDUCATIONAL','Thrifting, also known as thrift shopping or secondhand shopping, has existed for decades. For simplicity, thrift shopping is the practice of purchasing secondhand or used items from stores, either physical or online. Different people have different reasons for thrifting such as saving money, finding unexpected clothing and reducing carbon footprint. '),(3,'Ryan Yoo	\r\n','17 December 2018','What to do with broken lightbulbs?','GUIDELINES','Most people do not recycle lightbulbs, with good reasons. Firstly, they do not know that lightbulbs can be recycled. Secondly, they are unsure of the procedures to recycle lightbulb.\r\nIn this article, we will take a look at the different types of lightbulbs and see what we can do to recycle them.\r\nIncandescent bulbs and lamps can be thrown into the trash. However, if a bulb is broken, ensure that it is wrapped in paper or plastic before placing into the trash bin. Why? Simply, this prevents broken edges from cutting through garbage bag, resulting in a mess and helps prevent injury to our staff when filtering the items.\r\nLight-emitting diode (LED) bulbs do not contain mercury but are made with hazardous substances such as lead and arsenic. Careful handling is required as some recycling bins do not accept lead and arsenic light bulbs. In the event that LED bulbs are thrown without proper handling, the lead and arsenic might end up in the water stream.'),(4,'Jane Tan ','2 November 2021','Top 10 unexpected things to recycle','EDUCATIONAL','Recycling is an important practice for the environment. It helps to create sustainability for the future generation. Finding things that are recyclable is important for daily life. \r\n\r\n1. Cardboard boxes- these items fit into the paper category and can be recycled in meaningful ways. This is especially important for manufacturing companies, since cardboard boxes are mass-produced.'),(5,'Joseph Saw','5 January 2020','Our home is dying ','NEWS','The environmental impacts of our waste are immediate and continuous. Waste rotting in landfills can create a pungent-smelling methane gas that is both explosive and a huge contributor to global warming. Most people have misconception on the possibility of incinerating these waste without causing environment problems. However, gases produced from burning plastics produces toxic substances like dioxins and can cause air pollution and decrease pH level of the rain.'),(6,'James S','13 July 2018 ','5 ways to upcycle plastic bags','EDUCATIONAL','Despite our efforts to minimize our use of plastic bags, the bag always has a way of ending up in our homes and we\'ll throw them away and add to a mountain full of bags as seen from the Semakau landfill.');
/*!40000 ALTER TABLE `article` ENABLE KEYS */;
UNLOCK TABLES;


-- Dump completed on 2019-08-22 15:20:25
