import React, { useState, useEffect } from 'react';
import { 
  Layout, 
  Card, 
  Row, 
  Col, 
  Space, 
  Tag, 
  Avatar,
  Table,
  Switch,
  Segmented,
  Button, 
  Typography, 
  Statistic, 
  Divider, 
  message, 
  Dropdown,
  MenuProps,
  Input,
  Select,
  Pagination,
  Alert,
  Modal,
  List,
  Tooltip,
  Checkbox
} from 'antd';
import { 
  PushpinOutlined, 
  GlobalOutlined, 
  UserOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  EllipsisOutlined,
  MoreOutlined,
  ExpandAltOutlined,
  LinkOutlined,
  AppstoreOutlined,
  BarsOutlined,
  PlusOutlined,
  SearchOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  DownloadOutlined,
  CompressOutlined,
  TeamOutlined,
  CalendarOutlined,
  DollarOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import LabFormModal from './components/LabFormModal';
import PaperFormModal from './components/PaperFormModal';
import ResearchGroupManager from './components/ResearchGroupManager';
import './App.css';

const { Header, Content, Footer, Sider } = Layout;
const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

interface Lab {
  id: number;
  name: string;
  pi: string;
  institution: string;
  city?: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  focus_areas?: string[];
  website?: string;
  description?: string;
  established_year?: number;
  funding_sources?: string[];
  papers?: any[];
  paper_count?: number;
  lab_type?: string;
  parent_lab_id?: number;
  parent_lab?: string;
  sub_groups?: Lab[];
  sub_groups_count?: number;
}

interface Paper {
  id: number;
  title: string;
  authors: string;
  abstract?: string;
  publication_date?: string;
  venue?: string;
  paper_type?: string;
  arxiv_id?: string;
  doi?: string;
  pdf_url?: string;
  website_url?: string;
}

const App: React.FC = () => {
  const [labs, setLabs] = useState<Lab[]>([]);
  const [filteredLabs, setFilteredLabs] = useState<Lab[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedFocus, setSelectedFocus] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedLab, setSelectedLab] = useState<Lab | null>(null);
  const [expandedLabId, setExpandedLabId] = useState<number | null>(null);
  const [scrapeModalVisible, setScrapeModalVisible] = useState(false);
  const [selectedLabsForScraping, setSelectedLabsForScraping] = useState<number[]>([]);
  const [scrapingSources, setScrapingSources] = useState<string[]>(['arxiv']);
  const [scrapingInProgress, setScrapingInProgress] = useState(false);
  const [maxPapersToScrape, setMaxPapersToScrape] = useState<number>(5);
  const [institutionalPapers, setInstitutionalPapers] = useState<any[]>([]);
  
  // Paper form modal state
  const [paperModalVisible, setPaperModalVisible] = useState(false);
  const [paperModalMode, setPaperModalMode] = useState<'create' | 'edit'>('create');
  const [editingPaper, setEditingPaper] = useState<any>(null);
  const [selectedLabId, setSelectedLabId] = useState<number | null>(null);
  const [showInstitutionalScrapeModal, setShowInstitutionalScrapeModal] = useState(false);
  const [labFormVisible, setLabFormVisible] = useState(false);
  const [currentLab, setCurrentLab] = useState<Lab | null>(null);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [viewMode, setViewMode] = useState<'cards' | 'list'>('list');
  const [groupByInstitution, setGroupByInstitution] = useState(false);
  const [showChronologicalPapers, setShowChronologicalPapers] = useState(false);
  const [currentView, setCurrentView] = useState<'labs' | 'papers' | 'arxiv'>('labs');
  const [arxivPapers, setArxivPapers] = useState<any[]>([]);
  const [arxivLoading, setArxivLoading] = useState(false);
  const pageSize = 12;

  const loadLabs = async () => {
    try {
      setLoading(true);
      const url = 'http://127.0.0.1:8080/api/labs/?include_papers=true&include_sub_groups=true';
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Loaded labs:', data.length);
      setLabs(data);
      setFilteredLabs(data);
      setError(null);
    } catch (err) {
      setError('Failed to load robotics labs data');
      console.error('Error loading labs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLabs();
    loadArxivPapers();
  }, []);

  const loadArxivPapers = async () => {
    try {
      setArxivLoading(true);
      // Use our backend API to get ArXiv papers (avoids CORS issues)
      const response = await fetch('http://127.0.0.1:8080/api/labs/arxiv-latest');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setArxivPapers(data.papers || []);
    } catch (error) {
      console.error('Error fetching ArXiv papers:', error);
      // Fallback to empty array on error
      setArxivPapers([]);
    } finally {
      setArxivLoading(false);
    }
  };

  const handleScrapePapers = async () => {
    try {
      setScrapingInProgress(true);
      const response = await fetch('http://127.0.0.1:8080/api/labs/scrape-papers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lab_ids: selectedLabsForScraping,
          sources: scrapingSources,
          max_papers: maxPapersToScrape
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Scraping result:', result);
        
        // Reload labs data to show new papers
        const labsResponse = await fetch('http://127.0.0.1:8080/api/labs/?include_papers=true');
        if (labsResponse.ok) {
          const updatedLabs = await labsResponse.json();
          setLabs(updatedLabs);
          setFilteredLabs(updatedLabs);
        }
        
        setScrapeModalVisible(false);
        setSelectedLabsForScraping([]);
      } else {
        console.error('Scraping failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error during scraping:', error);
    } finally {
      setScrapingInProgress(false);
    }
  };

  const handleInstitutionalScraping = async () => {
    try {
      setScrapingInProgress(true);
      
      // Get unique institutions from current labs
      const institutions = Array.from(new Set(labs.map(lab => lab.institution)));
      
      const response = await fetch('http://127.0.0.1:8080/api/labs/scrape-institutional-papers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          institutions: institutions,
          max_papers: maxPapersToScrape
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Institutional scraping result:', result);
        
        if (result.papers && result.papers.length > 0) {
          setInstitutionalPapers(result.papers);
          message.success(`Found ${result.papers.length} papers from institutional search!`);
        } else {
          message.info('No new institutional papers found.');
        }
        
        setShowInstitutionalScrapeModal(false);
      } else {
        console.error('Institutional scraping failed:', response.statusText);
        message.error('Institutional scraping failed. Please try again.');
      }
    } catch (error) {
      console.error('Error during institutional scraping:', error);
      message.error('Error during institutional scraping.');
    } finally {
      setScrapingInProgress(false);
    }
  };

  // Paper management functions
  const handleAddPaper = (labId: number) => {
    setSelectedLabId(labId);
    setPaperModalMode('create');
    setEditingPaper(null);
    setPaperModalVisible(true);
  };

  const handleEditPaper = (paper: any) => {
    setSelectedLabId(paper.lab_id);
    setPaperModalMode('edit');
    setEditingPaper(paper);
    setPaperModalVisible(true);
  };

  const handleDeletePaper = async (paperId: number) => {
    try {
      const response = await fetch(`http://127.0.0.1:8080/api/papers/${paperId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        message.success('Paper deleted successfully');
        // Reload labs data to refresh papers
        const labsResponse = await fetch('http://127.0.0.1:8080/api/labs/?include_papers=true&include_sub_groups=true');
        const labsData = await labsResponse.json();
        setLabs(labsData);
      } else {
        throw new Error('Failed to delete paper');
      }
    } catch (error) {
      console.error('Error deleting paper:', error);
      message.error('Failed to delete paper');
    }
  };

  const handlePaperModalSuccess = async () => {
    setPaperModalVisible(false);
    setEditingPaper(null);
    setSelectedLabId(null);
    
    // Reload labs data to show updated papers
    const labsResponse = await fetch('http://127.0.0.1:8080/api/labs/?include_papers=true&include_sub_groups=true');
    const labsData = await labsResponse.json();
    setLabs(labsData);
  };

  const handlePaperModalCancel = () => {
    setPaperModalVisible(false);
    setEditingPaper(null);
    setSelectedLabId(null);
  };

  const handleCreateLab = () => {
    setCurrentLab(null);
    setFormMode('create');
    setLabFormVisible(true);
  };

  const handleEditLab = (lab: Lab) => {
    setCurrentLab(lab);
    setFormMode('edit');
    setLabFormVisible(true);
  };

  const handleDeleteLab = async (labId: number) => {
    try {
      const response = await fetch(`http://127.0.0.1:8080/api/labs/${labId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        message.success('Lab deleted successfully!');
        // Refresh the labs list
        const labsResponse = await fetch('http://127.0.0.1:8080/api/labs/?include_papers=true');
        if (labsResponse.ok) {
          const updatedLabs = await labsResponse.json();
          setLabs(updatedLabs);
          setFilteredLabs(updatedLabs);
        }
      } else {
        const error = await response.json();
        message.error(error.error || 'Delete failed');
      }
    } catch (error) {
      message.error('Network error occurred');
      console.error('Delete error:', error);
    }
  };

  const handleLabFormSuccess = async () => {
    // Refresh the labs list
    try {
      const response = await fetch('http://127.0.0.1:8080/api/labs/?include_papers=true');
      if (response.ok) {
        const updatedLabs = await response.json();
        setLabs(updatedLabs);
        setFilteredLabs(updatedLabs);
      }
    } catch (error) {
      console.error('Error refreshing labs:', error);
    }
    setLabFormVisible(false);
  };

  const getLabActions = (lab: Lab) => [
    {
      key: 'edit',
      label: 'Edit Lab',
      icon: <EditOutlined />,
      onClick: () => handleEditLab(lab),
    },
    {
      key: 'delete',
      label: 'Delete Lab',
      icon: <DeleteOutlined />,
      danger: true,
      onClick: () => {
        Modal.confirm({
          title: 'Delete Lab',
          content: `Are you sure you want to delete "${lab.name}"? This action cannot be undone.`,
          okText: 'Yes, Delete',
          okType: 'danger',
          cancelText: 'Cancel',
          onOk: () => handleDeleteLab(lab.id!),
        });
      },
    },
  ];

  const tableColumns = [
    {
      title: 'Lab',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Lab) => (
        <Space>
          <Avatar style={{ backgroundColor: '#1890ff' }}>
            {text.charAt(0)}
          </Avatar>
          <div>
            <div style={{ fontWeight: 'bold' }}>{text}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              {record.institution}
            </div>
          </div>
        </Space>
      ),
      sorter: (a: Lab, b: Lab) => a.name.localeCompare(b.name),
    },
    {
      title: 'PI',
      dataIndex: 'pi',
      key: 'pi',
      sorter: (a: Lab, b: Lab) => (a.pi || '').localeCompare(b.pi || ''),
    },
    {
      title: 'Location',
      key: 'location',
      render: (record: Lab) => `${record.city}, ${record.country}`,
      sorter: (a: Lab, b: Lab) => `${a.city}, ${a.country}`.localeCompare(`${b.city}, ${b.country}`),
    },
    {
      title: 'Focus Areas',
      dataIndex: 'focus_areas',
      key: 'focus_areas',
      render: (areas: string[]) => (
        <div>
          {areas && areas.slice(0, 2).map((area, index) => (
            <Tag key={index} color="geekblue" style={{ marginBottom: 2 }}>
              {area.length > 15 ? area.substring(0, 15) + '...' : area}
            </Tag>
          ))}
          {areas && areas.length > 2 && (
            <Tag color="default">+{areas.length - 2}</Tag>
          )}
        </div>
      ),
    },
    {
      title: 'Papers',
      dataIndex: 'paper_count',
      key: 'paper_count',
      render: (count: number) => (
        <div style={{ textAlign: 'center' }}>
          {count > 0 ? (
            <Tag color="green">{count} papers</Tag>
          ) : (
            <Tag color="default">No papers</Tag>
          )}
        </div>
      ),
      sorter: (a: Lab, b: Lab) => (a.paper_count || 0) - (b.paper_count || 0),
    },
    {
      title: 'Website',
      dataIndex: 'website',
      key: 'website',
      render: (website: string) => 
        website ? (
          <Button 
            type="link" 
            size="small"
            href={website} 
            target="_blank"
            icon={<LinkOutlined />}
          >
            Visit
          </Button>
        ) : null,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (record: Lab) => (
        <Dropdown
          menu={{ 
            items: getLabActions(record),
            onClick: ({ domEvent }) => {
              domEvent?.stopPropagation();
            }
          }}
          trigger={['click']}
        >
          <Button 
            type="text" 
            size="small"
            icon={<MoreOutlined />}
          />
        </Dropdown>
      ),
    },
  ];

  const handleCardClick = (lab: Lab) => {
    if (expandedLabId === lab.id) {
      setExpandedLabId(null);
      setSelectedLab(null);
    } else {
      setExpandedLabId(lab.id);
      setSelectedLab(lab);
    }
  };

  const formatAuthors = (authorsString: string) => {
    try {
      const authors = JSON.parse(authorsString);
      if (Array.isArray(authors)) {
        return authors.slice(0, 3).join(', ') + (authors.length > 3 ? ' et al.' : '');
      }
      return authorsString;
    } catch {
      return authorsString.split(',').slice(0, 3).join(', ') + (authorsString.split(',').length > 3 ? ' et al.' : '');
    }
  };

  // Filter labs based on search criteria
  useEffect(() => {
    let filtered = labs;

    if (searchTerm) {
      filtered = filtered.filter(lab =>
        lab.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lab.pi.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lab.institution.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedCountry) {
      filtered = filtered.filter(lab => lab.country === selectedCountry);
    }

    if (selectedFocus) {
      filtered = filtered.filter(lab => 
        lab.focus_areas && lab.focus_areas.some(area => 
          area.toLowerCase().includes(selectedFocus.toLowerCase())
        )
      );
    }

    setFilteredLabs(filtered);
    setCurrentPage(1);
  }, [searchTerm, selectedCountry, selectedFocus, labs]);

  // Get unique countries and focus areas for filters
  const countries = Array.from(new Set(labs.map(lab => lab.country))).sort();
  const allFocusAreas = labs.flatMap(lab => lab.focus_areas || []);
  const focusAreas = Array.from(new Set(allFocusAreas)).sort();

  // Group labs by institution if groupByInstitution is enabled
  const groupLabsByInstitution = (labs: Lab[]) => {
    const grouped = labs.reduce((acc, lab) => {
      const institution = lab.institution;
      if (!acc[institution]) {
        acc[institution] = [];
      }
      acc[institution].push(lab);
      return acc;
    }, {} as Record<string, Lab[]>);
    
    return Object.entries(grouped).sort((a, b) => b[1].length - a[1].length); // Sort by number of labs
  };

  // Get all papers from all labs in chronological order
  const getAllPapersChronologically = () => {
    const allPapers: (Paper & { lab: Lab })[] = [];
    
    labs.forEach(lab => {
      if (lab.papers && lab.papers.length > 0) {
        lab.papers.forEach(paper => {
          allPapers.push({
            ...paper,
            lab: lab
          });
        });
      }
    });
    
    // Sort by publication date (latest first)
    return allPapers.sort((a, b) => {
      const dateA = new Date(a.publication_date || '1900-01-01').getTime();
      const dateB = new Date(b.publication_date || '1900-01-01').getTime();
      return dateB - dateA;
    });
  };

  // Get labs for current page
  const startIndex = (currentPage - 1) * pageSize;
  const currentLabs = filteredLabs.slice(startIndex, startIndex + pageSize);
  const institutionGroups = groupByInstitution ? groupLabsByInstitution(filteredLabs) : [];

  return (
    <Layout className="app-layout">
      <Header style={{ background: '#001529', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Title level={2} style={{ color: 'white', margin: 0 }}>
          🤖 Robotics Research Trends - State of the Art
        </Title>
        <Space>
          <Segmented
            value={currentView}
            onChange={setCurrentView}
            options={[
              {
                label: (
                  <Space>
                    <GlobalOutlined />
                    <span>Labs</span>
                  </Space>
                ),
                value: 'labs',
              },
              {
                label: (
                  <Space>
                    <FileTextOutlined />
                    <span>All Papers</span>
                  </Space>
                ),
                value: 'papers',
              },
              {
                label: (
                  <Space>
                    <ExperimentOutlined />
                    <span>Latest ArXiv</span>
                  </Space>
                ),
                value: 'arxiv',
              },
            ]}
            size="large"
            style={{ backgroundColor: 'rgba(255,255,255,0.1)' }}
          />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateLab}
            size="large"
            style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
          >
            Add New Lab
          </Button>
        </Space>
      </Header>
      
      <Layout>
        <Sider width={300} style={{ background: '#fff', padding: '24px' }}>
          <Card title="Search & Filter" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Input
                placeholder="Search labs, PIs, institutions..."
                prefix={<SearchOutlined />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                allowClear
              />
              
              <Select
                placeholder="Filter by country"
                style={{ width: '100%' }}
                value={selectedCountry}
                onChange={setSelectedCountry}
                allowClear
              >
                {countries.map(country => (
                  <Option key={country} value={country}>{country}</Option>
                ))}
              </Select>
              
              <Select
                placeholder="Filter by focus area"
                style={{ width: '100%' }}
                value={selectedFocus}
                onChange={setSelectedFocus}
                allowClear
              >
                {focusAreas.slice(0, 20).map(focus => (
                  <Option key={focus} value={focus}>{focus}</Option>
                ))}
              </Select>
            </Space>
          </Card>

                    <Card title="Statistics" style={{ marginTop: 16 }} size="small">
            <Row gutter={[8, 8]}>
              <Col span={12}>
                <Statistic 
                  title="Total Labs" 
                  value={labs.length} 
                  prefix={<GlobalOutlined />} 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Countries" 
                  value={countries.length} 
                  prefix={<GlobalOutlined />} 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Papers" 
                  value={labs.reduce((sum, lab) => sum + (lab.paper_count || 0), 0)} 
                  prefix={<FileTextOutlined />} 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="With Papers" 
                  value={labs.filter(lab => (lab.paper_count || 0) > 0).length} 
                  prefix={<ExperimentOutlined />} 
                />
              </Col>
            </Row>
            
            <Button 
              type="primary" 
              block 
              style={{ marginTop: 16 }}
              onClick={() => setScrapeModalVisible(true)}
              icon={<DownloadOutlined />}
            >
              Scrape Latest Papers
            </Button>
            
            <Button 
              type="default" 
              block 
              style={{ marginTop: 8 }}
              onClick={() => setShowInstitutionalScrapeModal(true)}
              icon={<SearchOutlined />}
            >
              Find Other Lab Papers
            </Button>
          </Card>
        </Sider>

        <Content style={{ padding: '24px' }}>
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Card>
                <Title level={3}>Global Robotics Research Labs</Title>
                <Paragraph>
                  Interactive mapping of {labs.length} leading robotics research laboratories worldwide, 
                  tracking research trends, papers, and breakthrough technologies in robot learning, 
                  manipulation, perception, and autonomous systems.
                </Paragraph>
              </Card>
            </Col>
            
            <Col span={24}>
              {currentView === 'labs' ? (
                <Card 
                  title={groupByInstitution 
                    ? `Research Labs - ${institutionGroups.length} institutions (${filteredLabs.length} total labs)` 
                    : `Research Labs (${filteredLabs.length} results)`
                  } 
                  loading={loading}
                extra={
                  <Space size="large">
                    <Space>
                      <AppstoreOutlined />
                      <Switch
                        checked={viewMode === 'list'}
                        onChange={(checked) => setViewMode(checked ? 'list' : 'cards')}
                        checkedChildren="List"
                        unCheckedChildren="Cards"
                      />
                      <BarsOutlined />
                    </Space>
                    <Space>
                      <UserOutlined />
                      <Switch
                        checked={groupByInstitution}
                        onChange={(checked) => setGroupByInstitution(checked)}
                        checkedChildren="Grouped"
                        unCheckedChildren="Mixed"
                      />
                    </Space>
                    {!groupByInstitution && (
                      <Pagination
                        current={currentPage}
                        total={filteredLabs.length}
                        pageSize={pageSize}
                        onChange={setCurrentPage}
                        showSizeChanger={false}
                        showQuickJumper
                        showTotal={(total, range) => 
                          `${range[0]}-${range[1]} of ${total} labs`
                        }
                      />
                    )}
                  </Space>
                }
              >
                {error ? (
                  <Alert message={error} type="error" />
                ) : (
                  <div>
                    {groupByInstitution ? (
                      // Institution Grouped View
                      <div>
                        {institutionGroups.map(([institution, labs]) => (
                          <Card 
                            key={institution}
                            title={
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontSize: '18px', fontWeight: 'bold' }}>
                                  {institution}
                                </span>
                                <Tag color="blue">{labs.length} labs</Tag>
                              </div>
                            }
                            style={{ marginBottom: 16 }}
                            size="small"
                          >
                            <Row gutter={[16, 16]}>
                              {labs.map((lab) => {
                                const isExpanded = expandedLabId === lab.id;
                                return (
                                  <Col span={isExpanded ? 24 : 8} key={lab.id}>
                                    <Card 
                                      size="small" 
                                      className={`lab-card ${isExpanded ? 'expanded' : ''}`}
                                      title={
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                            <Avatar style={{ backgroundColor: '#1890ff' }}>
                                              {lab.name.charAt(0)}
                                            </Avatar>
                                            <span style={{ fontSize: isExpanded ? '18px' : '14px', fontWeight: 'bold' }}>
                                              {isExpanded ? lab.name : (lab.name.length > 30 ? lab.name.substring(0, 30) + '...' : lab.name)}
                                            </span>
                                          </div>
                                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                            {lab.paper_count && lab.paper_count > 0 && (
                                              <Tag color="green">{lab.paper_count} papers</Tag>
                                            )}
                                            <Button 
                                              type="text" 
                                              size="small"
                                              icon={isExpanded ? <CompressOutlined /> : <ExpandAltOutlined />}
                                              onClick={(e) => {
                                                e.stopPropagation();
                                                handleCardClick(lab);
                                              }}
                                            />
                                          </div>
                                        </div>
                                      }
                                      style={{ 
                                        height: isExpanded ? 'auto' : '250px',
                                        cursor: 'pointer',
                                        border: isExpanded ? '2px solid #1890ff' : '1px solid #d9d9d9',
                                        transition: 'all 0.3s ease'
                                      }}
                                      onClick={() => handleCardClick(lab)}
                                      hoverable
                                    >
                                      {isExpanded ? (
                                        // Expanded view - simplified version
                                        <div>
                                          <Row gutter={[24, 16]}>
                                            <Col span={12}>
                                              <Card title="Lab Information" size="small">
                                                <Space direction="vertical" style={{ width: '100%' }}>
                                                  <div>
                                                    <strong>Principal Investigator:</strong>
                                                    <div style={{ marginTop: 4 }}>
                                                      <Avatar size="small" style={{ backgroundColor: '#52c41a', marginRight: 8 }}>
                                                        <TeamOutlined />
                                                      </Avatar>
                                                      {lab.pi}
                                                    </div>
                                                  </div>
                                                  <div>
                                                    <strong>Institution:</strong>
                                                    <div style={{ marginTop: 4 }}>{lab.institution}</div>
                                                  </div>
                                                  <div>
                                                    <strong>Location:</strong>
                                                    <div style={{ marginTop: 4 }}>
                                                      <PushpinOutlined /> {lab.city}, {lab.country}
                                                    </div>
                                                  </div>
                                                  {lab.website && (
                                                    <div>
                                                      <strong>Website:</strong>
                                                      <div style={{ marginTop: 4 }}>
                                                        <a href={lab.website} target="_blank" rel="noopener noreferrer">
                                                          <LinkOutlined /> Visit Lab Website
                                                        </a>
                                                      </div>
                                                    </div>
                                                  )}
                                                </Space>
                                              </Card>
                                            </Col>
                                            <Col span={12}>
                                              <Card title="Research Focus" size="small">
                                                {lab.focus_areas && lab.focus_areas.length > 0 ? (
                                                  <div style={{ marginBottom: 16 }}>
                                                    {lab.focus_areas.map((area, index) => (
                                                      <Tag key={index} color="blue" style={{ marginBottom: 4 }}>
                                                        {area}
                                                      </Tag>
                                                    ))}
                                                  </div>
                                                ) : (
                                                  <p>No focus areas specified</p>
                                                )}
                                                
                                                {lab.description && (
                                                  <div>
                                                    <strong>Description:</strong>
                                                    <div style={{ marginTop: 4, color: '#666' }}>
                                                      {lab.description}
                                                    </div>
                                                  </div>
                                                )}
                                              </Card>
                                            </Col>
                                          </Row>
                                          
                                          {lab.papers && lab.papers.length > 0 && (
                                            <Card 
                                              title={`Recent Papers (${lab.papers.length})`}
                                              extra={
                                                <Button 
                                                  type="primary" 
                                                  size="small" 
                                                  icon={<PlusOutlined />}
                                                  onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleAddPaper(lab.id);
                                                  }}
                                                >
                                                  Add Paper
                                                </Button>
                                              }
                                              style={{ marginTop: 16 }} 
                                              size="small"
                                            >
                                              <List
                                                itemLayout="vertical"
                                                dataSource={lab.papers?.sort((a, b) => new Date(b.publication_date).getTime() - new Date(a.publication_date).getTime())}
                                                renderItem={(paper, index) => (
                                                  <List.Item
                                                    key={index}
                                                    actions={[
                                                      paper.pdf_url && (
                                                        <Button 
                                                          type="link" 
                                                          href={paper.pdf_url}
                                                          target="_blank"
                                                          onClick={(e) => e.stopPropagation()}
                                                          icon={<FileTextOutlined />}
                                                        >
                                                          PDF
                                                        </Button>
                                                      ),
                                                      paper.arxiv_id && (
                                                        <Button 
                                                          type="link" 
                                                          href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                                                          target="_blank"
                                                          onClick={(e) => e.stopPropagation()}
                                                          icon={<LinkOutlined />}
                                                        >
                                                          ArXiv
                                                        </Button>
                                                      ),
                                                      <Button 
                                                        type="link" 
                                                        onClick={(e) => {
                                                          e.stopPropagation();
                                                          handleEditPaper(paper);
                                                        }}
                                                        icon={<EditOutlined />}
                                                      >
                                                        Edit
                                                      </Button>,
                                                      <Button 
                                                        type="link" 
                                                        danger
                                                        onClick={(e) => {
                                                          e.stopPropagation();
                                                          Modal.confirm({
                                                            title: 'Delete Paper',
                                                            content: `Are you sure you want to delete "${paper.title}"?`,
                                                            onOk: () => handleDeletePaper(paper.id),
                                                          });
                                                        }}
                                                        icon={<DeleteOutlined />}
                                                      >
                                                        Delete
                                                      </Button>
                                                    ].filter(Boolean)}
                                                  >
                                                    <List.Item.Meta
                                                      title={
                                                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                                          {paper.title}
                                                        </div>
                                                      }
                                                      description={
                                                        <div>
                                                          <div style={{ marginBottom: 4 }}>
                                                            <strong>Authors:</strong> {formatAuthors(paper.authors)}
                                                          </div>
                                                          {paper.venue && (
                                                            <div style={{ marginBottom: 4 }}>
                                                              <strong>Venue:</strong> {paper.venue}
                                                            </div>
                                                          )}
                                                          {paper.publication_date && (
                                                            <div style={{ marginBottom: 4 }}>
                                                              <strong>Date:</strong> {new Date(paper.publication_date).toLocaleDateString()}
                                                            </div>
                                                          )}
                                                          {paper.abstract && (
                                                            <div style={{ marginTop: 8, padding: 8, background: '#f9f9f9', borderRadius: 4 }}>
                                                              <strong>Abstract:</strong> {paper.abstract.length > 300 ? paper.abstract.substring(0, 300) + '...' : paper.abstract}
                                                            </div>
                                                          )}
                                                        </div>
                                                      }
                                                    />
                                                  </List.Item>
                                                )}
                                              />
                                            </Card>
                                          )}
                                          
                                          {(!lab.papers || lab.papers.length === 0) && (
                                            <Card 
                                              title="Papers"
                                              extra={
                                                <Button 
                                                  type="primary" 
                                                  size="small" 
                                                  icon={<PlusOutlined />}
                                                  onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleAddPaper(lab.id);
                                                  }}
                                                >
                                                  Add First Paper
                                                </Button>
                                              }
                                              style={{ marginTop: 16 }} 
                                              size="small"
                                            >
                                              <p style={{ color: '#666', textAlign: 'center', margin: 16 }}>
                                                No papers yet. Click "Add First Paper" to get started.
                                              </p>
                                            </Card>
                                          )}
                                          
                                          {lab.sub_groups_count && lab.sub_groups_count > 0 && (
                                            <Card title="Research Groups" size="small" style={{ marginTop: 16 }}>
                                              <ResearchGroupManager 
                                                lab={lab}
                                                onGroupCreated={loadLabs}
                                              />
                                            </Card>
                                          )}
                                        </div>
                                      ) : (
                                        // Collapsed view
                                        <>
                                          <div style={{ marginBottom: 8 }}>
                                            <strong>PI:</strong> {lab.pi}
                                          </div>
                                          <div style={{ marginBottom: 8 }}>
                                            <strong>Location:</strong> {lab.city}, {lab.country}
                                          </div>
                                          {lab.focus_areas && lab.focus_areas.length > 0 && (
                                            <div style={{ marginBottom: 8 }}>
                                              <strong>Focus Areas:</strong>
                                              <div style={{ marginTop: 4 }}>
                                                {lab.focus_areas.slice(0, 3).map((area, index) => (
                                                  <Tag key={index} style={{ marginBottom: 2, fontSize: '12px' }}>
                                                    {area}
                                                  </Tag>
                                                ))}
                                                {lab.focus_areas.length > 3 && (
                                                  <Tag style={{ marginBottom: 2, fontSize: '12px' }}>
                                                    +{lab.focus_areas.length - 3} more
                                                  </Tag>
                                                )}
                                              </div>
                                            </div>
                                          )}
                                        </>
                                      )}
                                    </Card>
                                  </Col>
                                );
                              })}
                            </Row>
                          </Card>
                        ))}
                      </div>
                    ) : (
                      // Normal View (non-grouped)
                      <>
                        {viewMode === 'cards' ? (
                      // Card View
                      <Row gutter={[16, 16]}>
                        {currentLabs.map((lab) => {
                          const isExpanded = expandedLabId === lab.id;
                          return (
                            <Col span={isExpanded ? 24 : 8} key={lab.id}>
                              <Card 
                                size="small" 
                                className={`lab-card ${isExpanded ? 'expanded' : ''}`}
                                title={
                                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                      <Avatar style={{ backgroundColor: '#1890ff' }}>
                                        {lab.name.charAt(0)}
                                      </Avatar>
                                      <span style={{ fontSize: isExpanded ? '18px' : '14px', fontWeight: 'bold' }}>
                                        {isExpanded ? lab.name : (lab.name.length > 30 ? lab.name.substring(0, 30) + '...' : lab.name)}
                                      </span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                      {lab.paper_count && lab.paper_count > 0 && (
                                        <Tag color="green">{lab.paper_count} papers</Tag>
                                      )}
                                      <Button 
                                        type="text" 
                                        size="small"
                                        icon={isExpanded ? <CompressOutlined /> : <ExpandAltOutlined />}
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleCardClick(lab);
                                        }}
                                      />
                                      <Dropdown
                                        menu={{ 
                                          items: getLabActions(lab),
                                          onClick: ({ domEvent }) => {
                                            domEvent?.stopPropagation();
                                          }
                                        }}
                                        trigger={['click']}
                                      >
                                        <Button 
                                          type="text" 
                                          size="small"
                                          icon={<MoreOutlined />}
                                          onClick={(e) => e.stopPropagation()}
                                        />
                                      </Dropdown>
                                    </div>
                                  </div>
                                }
                                style={{ 
                                  height: isExpanded ? 'auto' : '400px',
                                  cursor: 'pointer',
                                  border: isExpanded ? '2px solid #1890ff' : '1px solid #d9d9d9',
                                  transition: 'all 0.3s ease'
                                }}
                                onClick={() => handleCardClick(lab)}
                                hoverable
                              >
                                {isExpanded ? (
                                  // Expanded view
                                  <div>
                                    <Row gutter={[24, 16]}>
                                      <Col span={12}>
                                        <Card title="Lab Information" size="small">
                                          <Space direction="vertical" style={{ width: '100%' }}>
                                            <div>
                                              <strong>Principal Investigator:</strong>
                                              <div style={{ marginTop: 4 }}>
                                                <Avatar size="small" style={{ backgroundColor: '#52c41a', marginRight: 8 }}>
                                                  <TeamOutlined />
                                                </Avatar>
                                                {lab.pi}
                                              </div>
                                            </div>
                                            
                                            <div>
                                              <strong>Institution:</strong>
                                              <div style={{ marginTop: 4 }}>{lab.institution}</div>
                                            </div>
                                            
                                            <div>
                                              <strong>Location:</strong>
                                              <div style={{ marginTop: 4 }}>
                                                <GlobalOutlined style={{ marginRight: 8 }} />
                                                {lab.city}, {lab.country}
                                              </div>
                                            </div>
                                            
                                            {lab.established_year && (
                                              <div>
                                                <strong>Established:</strong>
                                                <div style={{ marginTop: 4 }}>
                                                  <CalendarOutlined style={{ marginRight: 8 }} />
                                                  {lab.established_year}
                                                </div>
                                              </div>
                                            )}
                                            
                                            {lab.description && (
                                              <div>
                                                <strong>Description:</strong>
                                                <div style={{ marginTop: 4, padding: 8, background: '#f5f5f5', borderRadius: 4 }}>
                                                  {lab.description}
                                                </div>
                                              </div>
                                            )}
                                            
                                            <div style={{ display: 'flex', gap: 8 }}>
                                              {lab.website && (
                                                <Button 
                                                  type="primary"
                                                  href={lab.website} 
                                                  target="_blank"
                                                  icon={<LinkOutlined />}
                                                  onClick={(e) => e.stopPropagation()}
                                                >
                                                  Visit Lab
                                                </Button>
                                              )}
                                            </div>
                                          </Space>
                                        </Card>
                                      </Col>
                                      
                                      <Col span={12}>
                                        <Card title="Research Focus" size="small">
                                          {lab.focus_areas && lab.focus_areas.length > 0 ? (
                                            <div>
                                              {lab.focus_areas.map((area, index) => (
                                                <Tag key={index} color="geekblue" style={{ marginBottom: 4 }}>
                                                  {area}
                                                </Tag>
                                              ))}
                                            </div>
                                          ) : (
                                            <div style={{ color: '#999' }}>No focus areas specified</div>
                                          )}
                                          
                                          {lab.funding_sources && lab.funding_sources.length > 0 && (
                                            <div style={{ marginTop: 16 }}>
                                              <strong>Funding Sources:</strong>
                                              <div style={{ marginTop: 8 }}>
                                                {lab.funding_sources.map((source, index) => (
                                                  <Tag key={index} color="orange" style={{ marginBottom: 4 }}>
                                                    <DollarOutlined style={{ marginRight: 4 }} />
                                                    {source}
                                                  </Tag>
                                                ))}
                                              </div>
                                            </div>
                                          )}
                                        </Card>
                                      </Col>
                                    </Row>
                                    
                                    {lab.papers && lab.papers.length > 0 && (
                                      <Card 
                                        title={`Recent Papers (${lab.papers.length})`}
                                        extra={
                                          <Button 
                                            type="primary" 
                                            size="small" 
                                            icon={<PlusOutlined />}
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              handleAddPaper(lab.id);
                                            }}
                                          >
                                            Add Paper
                                          </Button>
                                        }
                                        style={{ marginTop: 16 }} 
                                        size="small"
                                      >
                                        <List
                                          itemLayout="vertical"
                                          dataSource={lab.papers?.sort((a, b) => new Date(b.publication_date).getTime() - new Date(a.publication_date).getTime())}
                                          renderItem={(paper, index) => (
                                            <List.Item
                                              key={index}
                                              actions={[
                                                paper.pdf_url && (
                                                  <Button 
                                                    type="link" 
                                                    href={paper.pdf_url}
                                                    target="_blank"
                                                    onClick={(e) => e.stopPropagation()}
                                                    icon={<FileTextOutlined />}
                                                  >
                                                    PDF
                                                  </Button>
                                                ),
                                                paper.arxiv_id && (
                                                  <Button 
                                                    type="link" 
                                                    href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                                                    target="_blank"
                                                    onClick={(e) => e.stopPropagation()}
                                                    icon={<LinkOutlined />}
                                                  >
                                                    ArXiv
                                                  </Button>
                                                ),
                                                <Button 
                                                  type="link" 
                                                  onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleEditPaper(paper);
                                                  }}
                                                  icon={<EditOutlined />}
                                                >
                                                  Edit
                                                </Button>,
                                                <Button 
                                                  type="link" 
                                                  danger
                                                  onClick={(e) => {
                                                    e.stopPropagation();
                                                    Modal.confirm({
                                                      title: 'Delete Paper',
                                                      content: `Are you sure you want to delete "${paper.title}"?`,
                                                      onOk: () => handleDeletePaper(paper.id),
                                                    });
                                                  }}
                                                  icon={<DeleteOutlined />}
                                                >
                                                  Delete
                                                </Button>
                                              ].filter(Boolean)}
                                            >
                                              <List.Item.Meta
                                                title={
                                                  <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                                    {paper.title}
                                                  </div>
                                                }
                                                description={
                                                  <div>
                                                    <div style={{ marginBottom: 4 }}>
                                                      <strong>Authors:</strong> {formatAuthors(paper.authors)}
                                                    </div>
                                                    {paper.venue && (
                                                      <div style={{ marginBottom: 4 }}>
                                                        <strong>Venue:</strong> {paper.venue}
                                                      </div>
                                                    )}
                                                    {paper.publication_date && (
                                                      <div style={{ marginBottom: 4 }}>
                                                        <strong>Date:</strong> {new Date(paper.publication_date).toLocaleDateString()}
                                                      </div>
                                                    )}
                                                    {paper.abstract && (
                                                      <div style={{ marginTop: 8, padding: 8, background: '#f9f9f9', borderRadius: 4 }}>
                                                        <strong>Abstract:</strong> {paper.abstract.length > 300 ? paper.abstract.substring(0, 300) + '...' : paper.abstract}
                                                      </div>
                                                    )}
                                                  </div>
                                                }
                                              />
                                            </List.Item>
                                          )}
                                        />
                                      </Card>
                                    )}
                                    
                                    {(!lab.papers || lab.papers.length === 0) && (
                                      <Card 
                                        title="Papers"
                                        extra={
                                          <Button 
                                            type="primary" 
                                            size="small" 
                                            icon={<PlusOutlined />}
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              handleAddPaper(lab.id);
                                            }}
                                          >
                                            Add First Paper
                                          </Button>
                                        }
                                        style={{ marginTop: 16 }} 
                                        size="small"
                                      >
                                        <p style={{ color: '#666', textAlign: 'center', margin: 16 }}>
                                          No papers yet. Click "Add First Paper" to get started.
                                        </p>
                                      </Card>
                                    )}
                                    
                                    <ResearchGroupManager 
                                      lab={lab} 
                                      onGroupCreated={loadLabs}
                                    />
                                  </div>
                                ) : (
                                  // Collapsed view
                                  <div style={{ height: '340px', overflowY: 'auto' }}>
                                    <p><strong>PI:</strong> {lab.pi}</p>
                                    <p><strong>Institution:</strong> {
                                      lab.institution.length > 25 ? 
                                      lab.institution.substring(0, 25) + '...' : 
                                      lab.institution
                                    }</p>
                                    <p><strong>Location:</strong> {lab.city}, {lab.country}</p>
                                    
                                    {lab.focus_areas && lab.focus_areas.length > 0 && (
                                      <div style={{ marginTop: 8 }}>
                                        <strong>Focus:</strong>
                                        <div style={{ marginTop: 4 }}>
                                          {lab.focus_areas.slice(0, 2).map((area, index) => (
                                            <Tag key={index} color="geekblue" style={{ marginBottom: 4 }}>
                                              {area.length > 12 ? area.substring(0, 12) + '...' : area}
                                            </Tag>
                                          ))}
                                          {lab.focus_areas.length > 2 && (
                                            <Tag color="default">
                                              +{lab.focus_areas.length - 2}
                                            </Tag>
                                          )}
                                        </div>
                                      </div>
                                    )}
                                    
                                    {lab.papers && lab.papers.length > 0 && (
                                      <div style={{ marginTop: 12 }}>
                                        <Divider style={{ margin: '8px 0' }}>Recent Papers</Divider>
                                        {lab.papers
                                          .sort((a, b) => new Date(b.publication_date).getTime() - new Date(a.publication_date).getTime())
                                          .slice(0, 2)
                                          .map((paper, index) => (
                                          <div key={index} className="paper-item" style={{ marginBottom: 8, padding: 6, background: '#f9f9f9', borderRadius: 4 }}>
                                            <Tooltip title={paper.title}>
                                              <div style={{ fontWeight: 'bold', fontSize: '12px', marginBottom: 2 }}>
                                                {paper.title.length > 60 ? paper.title.substring(0, 60) + '...' : paper.title}
                                              </div>
                                            </Tooltip>
                                            <div style={{ fontSize: '11px', color: '#666' }}>
                                              {paper.venue && (
                                                <span>{paper.venue} • </span>
                                              )}
                                              {paper.publication_date && (
                                                <span>{new Date(paper.publication_date).getFullYear()}</span>
                                              )}
                                            </div>
                                            {(paper.pdf_url || paper.arxiv_id) && (
                                              <Button 
                                                type="link" 
                                                size="small"
                                                href={paper.pdf_url || `https://arxiv.org/abs/${paper.arxiv_id}`}
                                                target="_blank"
                                                onClick={(e) => e.stopPropagation()}
                                                style={{ padding: 0, height: 'auto', fontSize: '11px' }}
                                              >
                                                View PDF →
                                              </Button>
                                            )}
                                          </div>
                                        ))}
                                        {lab.papers.length > 2 && (
                                          <div style={{ textAlign: 'center', fontSize: '12px', color: '#666' }}>
                                            +{lab.papers.length - 2} more papers (click to expand)
                                          </div>
                                        )}
                                      </div>
                                    )}
                                    
                                    {lab.website && (
                                      <div style={{ position: 'absolute', bottom: 8, left: 16, right: 16 }}>
                                        <Button 
                                          type="link" 
                                          size="small"
                                          href={lab.website} 
                                          target="_blank"
                                          onClick={(e) => e.stopPropagation()}
                                          style={{ padding: 0 }}
                                          icon={<LinkOutlined />}
                                        >
                                          Visit Lab
                                        </Button>
                                      </div>
                                    )}
                                  </div>
                                )}
                              </Card>
                            </Col>
                          );
                        })}
                        
                        {/* Institutional Papers Card (Other Labs) */}
                        {institutionalPapers.length > 0 && (
                          <Col span={8} key="institutional-papers">
                            <Card 
                              size="small" 
                              className="lab-card"
                              title={
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <Avatar style={{ backgroundColor: '#722ed1' }}>
                                      🌐
                                    </Avatar>
                                    <span style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                      Other Labs
                                    </span>
                                  </div>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <Tag color="purple">{institutionalPapers.length} papers</Tag>
                                  </div>
                                </div>
                              }
                              style={{ 
                                height: '250px',
                                cursor: 'default',
                                border: '1px solid #722ed1',
                              }}
                            >
                              <div style={{ height: '160px', overflowY: 'auto' }}>
                                <p><strong>Recent papers found from institutional searches:</strong></p>
                                
                                {institutionalPapers.slice(0, 2).map((paper, index) => (
                                  <div key={index} style={{ marginBottom: 12, padding: 8, background: '#f9f9f9', borderRadius: 4 }}>
                                    <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: 4 }}>
                                      {paper.title.length > 50 ? paper.title.substring(0, 50) + '...' : paper.title}
                                    </div>
                                    <div style={{ fontSize: '11px', color: '#666', marginBottom: 4 }}>
                                      <strong>Authors:</strong> {formatAuthors(paper.authors)}
                                    </div>
                                    {paper.publication_date && (
                                      <div style={{ fontSize: '11px', color: '#999' }}>
                                        {new Date(paper.publication_date).getFullYear()}
                                      </div>
                                    )}
                                    {paper.pdf_url && (
                                      <Button 
                                        type="link" 
                                        size="small"
                                        href={paper.pdf_url}
                                        target="_blank"
                                        style={{ padding: 0, height: 'auto', fontSize: '11px' }}
                                      >
                                        View PDF →
                                      </Button>
                                    )}
                                  </div>
                                ))}
                                {institutionalPapers.length > 2 && (
                                  <div style={{ textAlign: 'center', fontSize: '12px', color: '#666' }}>
                                    +{institutionalPapers.length - 2} more papers discovered
                                  </div>
                                )}
                              </div>
                            </Card>
                          </Col>
                        )}
                      </Row>
                    ) : (
                      // List View
                      <Table
                        columns={tableColumns}
                        dataSource={currentLabs}
                        pagination={false}
                        rowKey="id"
                        size="middle"
                        scroll={{ x: 1200 }}
                        expandable={{
                          expandedRowKeys: expandedLabId ? [expandedLabId] : [],
                          onExpand: (expanded, record) => {
                            setExpandedLabId(expanded ? record.id : null);
                          },
                          expandedRowRender: (record) => (
                            <div style={{ padding: '16px', backgroundColor: '#fafafa' }}>
                              <Row gutter={[24, 16]}>
                                <Col span={12}>
                                  <Card title="Lab Information" size="small">
                                    <Space direction="vertical" style={{ width: '100%' }}>
                                      <div>
                                        <strong>Principal Investigator:</strong>
                                        <div style={{ marginTop: 4 }}>
                                          <Avatar size="small" style={{ backgroundColor: '#52c41a', marginRight: 8 }}>
                                            <TeamOutlined />
                                          </Avatar>
                                          {record.pi}
                                        </div>
                                      </div>
                                      
                                      <div>
                                        <strong>Institution:</strong>
                                        <div style={{ marginTop: 4 }}>{record.institution}</div>
                                      </div>
                                      
                                      <div>
                                        <strong>Location:</strong>
                                        <div style={{ marginTop: 4 }}>
                                          <GlobalOutlined style={{ marginRight: 8 }} />
                                          {record.city}, {record.country}
                                        </div>
                                      </div>
                                      
                                      {record.established_year && (
                                        <div>
                                          <strong>Established:</strong>
                                          <div style={{ marginTop: 4 }}>
                                            <CalendarOutlined style={{ marginRight: 8 }} />
                                            {record.established_year}
                                          </div>
                                        </div>
                                      )}
                                      
                                      {record.description && (
                                        <div>
                                          <strong>Description:</strong>
                                          <div style={{ marginTop: 4, padding: 8, background: '#f5f5f5', borderRadius: 4 }}>
                                            {record.description}
                                          </div>
                                        </div>
                                      )}
                                      
                                      <div style={{ display: 'flex', gap: 8 }}>
                                        {record.website && (
                                          <Button 
                                            type="primary"
                                            href={record.website} 
                                            target="_blank"
                                            icon={<LinkOutlined />}
                                          >
                                            Visit Lab
                                          </Button>
                                        )}
                                      </div>
                                    </Space>
                                  </Card>
                                </Col>
                                
                                <Col span={12}>
                                  <Card title="Research Focus" size="small">
                                    {record.focus_areas && record.focus_areas.length > 0 ? (
                                      <div>
                                        {record.focus_areas.map((area, index) => (
                                          <Tag key={index} color="geekblue" style={{ marginBottom: 4 }}>
                                            {area}
                                          </Tag>
                                        ))}
                                      </div>
                                    ) : (
                                      <div style={{ color: '#999' }}>No focus areas specified</div>
                                    )}
                                    
                                    {record.funding_sources && record.funding_sources.length > 0 && (
                                      <div style={{ marginTop: 16 }}>
                                        <strong>Funding Sources:</strong>
                                        <div style={{ marginTop: 8 }}>
                                          {record.funding_sources.map((source, index) => (
                                            <Tag key={index} color="orange" style={{ marginBottom: 4 }}>
                                              <DollarOutlined style={{ marginRight: 4 }} />
                                              {source}
                                            </Tag>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                  </Card>
                                </Col>
                              </Row>
                              
                              {record.papers && record.papers.length > 0 && (
                                <Card 
                                  title={`Recent Papers (${record.papers.length})`}
                                  extra={
                                    <Button 
                                      type="primary" 
                                      size="small" 
                                      icon={<PlusOutlined />}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleAddPaper(record.id);
                                      }}
                                    >
                                      Add Paper
                                    </Button>
                                  }
                                  style={{ marginTop: 16 }} 
                                  size="small"
                                >
                                  <List
                                    itemLayout="vertical"
                                    dataSource={record.papers}
                                    renderItem={(paper, index) => (
                                      <List.Item
                                        key={index}
                                        actions={[
                                          paper.pdf_url && (
                                            <Button 
                                              type="link" 
                                              href={paper.pdf_url}
                                              target="_blank"
                                              icon={<FileTextOutlined />}
                                            >
                                              PDF
                                            </Button>
                                          ),
                                          paper.arxiv_id && (
                                            <Button 
                                              type="link" 
                                              href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                                              target="_blank"
                                              icon={<LinkOutlined />}
                                            >
                                              ArXiv
                                            </Button>
                                          ),
                                          <Button 
                                            type="link" 
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              handleEditPaper(paper);
                                            }}
                                            icon={<EditOutlined />}
                                          >
                                            Edit
                                          </Button>,
                                          <Button 
                                            type="link" 
                                            danger
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              Modal.confirm({
                                                title: 'Delete Paper',
                                                content: `Are you sure you want to delete "${paper.title}"?`,
                                                onOk: () => handleDeletePaper(paper.id),
                                              });
                                            }}
                                            icon={<DeleteOutlined />}
                                          >
                                            Delete
                                          </Button>
                                        ].filter(Boolean)}
                                      >
                                        <List.Item.Meta
                                          title={
                                            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                                              {paper.title}
                                            </div>
                                          }
                                          description={
                                            <div>
                                              <div style={{ marginBottom: 4 }}>
                                                <strong>Authors:</strong> {formatAuthors(paper.authors)}
                                              </div>
                                              {paper.venue && (
                                                <div style={{ marginBottom: 4 }}>
                                                  <strong>Venue:</strong> {paper.venue}
                                                </div>
                                              )}
                                              {paper.publication_date && (
                                                <div style={{ marginBottom: 4 }}>
                                                  <strong>Date:</strong> {new Date(paper.publication_date).toLocaleDateString()}
                                                </div>
                                              )}
                                              {paper.abstract && (
                                                <div style={{ marginTop: 8, padding: 8, background: '#f9f9f9', borderRadius: 4 }}>
                                                  <strong>Abstract:</strong> {paper.abstract.length > 300 ? paper.abstract.substring(0, 300) + '...' : paper.abstract}
                                                </div>
                                              )}
                                            </div>
                                          }
                                        />
                                      </List.Item>
                                    )}
                                  />
                                </Card>
                              )}
                              
                              {(!record.papers || record.papers.length === 0) && (
                                <Card 
                                  title="Papers"
                                  extra={
                                    <Button 
                                      type="primary" 
                                      size="small" 
                                      icon={<PlusOutlined />}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleAddPaper(record.id);
                                      }}
                                    >
                                      Add First Paper
                                    </Button>
                                  }
                                  style={{ marginTop: 16 }} 
                                  size="small"
                                >
                                  <p style={{ color: '#666', textAlign: 'center', margin: 16 }}>
                                    No papers yet. Click "Add First Paper" to get started.
                                  </p>
                                </Card>
                              )}
                            </div>
                          ),
                          expandIcon: ({ expanded, onExpand, record }) => (
                            <Button
                              type="text"
                              size="small"
                              icon={expanded ? <CompressOutlined /> : <ExpandAltOutlined />}
                              onClick={(e) => {
                                e.stopPropagation();
                                onExpand(record, e);
                              }}
                              title={expanded ? "Collapse" : "Expand Details"}
                            />
                          ),
                        }}
                      />
                    )}
                    
                    {filteredLabs.length === 0 && !loading && (
                      <div style={{ textAlign: 'center', padding: '40px' }}>
                        <Title level={4}>No labs found</Title>
                        <Paragraph>Try adjusting your search criteria</Paragraph>
                      </div>
                    )}
                      </>
                    )}
                  </div>
                )}
              </Card>
              ) : currentView === 'papers' ? (
                <Card 
                  title={`All Papers - Chronological View (${getAllPapersChronologically().length} papers)`}
                  loading={loading}
                >
                  <List
                    itemLayout="vertical"
                    size="large"
                    pagination={{
                      onChange: (page) => setCurrentPage(page),
                      pageSize: 20,
                      showSizeChanger: true,
                      showQuickJumper: true,
                      showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} papers`,
                    }}
                    dataSource={getAllPapersChronologically()}
                    renderItem={(paper: Paper & { lab: Lab }) => (
                      <List.Item
                        key={`${paper.lab.id}-${paper.id}`}
                        actions={[
                          <Space key="actions">
                            {paper.pdf_url && (
                              <Button
                                type="link"
                                icon={<FileTextOutlined />}
                                href={paper.pdf_url}
                                target="_blank"
                                size="small"
                              >
                                PDF
                              </Button>
                            )}
                            {paper.arxiv_id && (
                              <Button
                                type="link"
                                href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                                target="_blank"
                                size="small"
                              >
                                ArXiv
                              </Button>
                            )}
                            {paper.doi && (
                              <Button
                                type="link"
                                href={`https://doi.org/${paper.doi}`}
                                target="_blank"
                                size="small"
                              >
                                DOI
                              </Button>
                            )}
                          </Space>
                        ]}
                        extra={
                          <Space direction="vertical" align="end">
                            <Tag color="blue">{paper.lab.name}</Tag>
                            <Tag color="green">{paper.lab.institution}</Tag>
                            {paper.venue && <Tag color="orange">{paper.venue}</Tag>}
                            {paper.publication_date && (
                              <Text type="secondary">
                                <CalendarOutlined /> {new Date(paper.publication_date).toLocaleDateString()}
                              </Text>
                            )}
                          </Space>
                        }
                      >
                        <List.Item.Meta
                          title={
                            <Space>
                              <Text strong style={{ fontSize: '16px' }}>
                                {paper.title}
                              </Text>
                              {paper.paper_type && (
                                <Tag color={
                                  paper.paper_type === 'journal' ? 'red' :
                                  paper.paper_type === 'conference' ? 'blue' :
                                  paper.paper_type === 'preprint' ? 'orange' : 'default'
                                }>
                                  {paper.paper_type}
                                </Tag>
                              )}
                            </Space>
                          }
                          description={
                            <Space direction="vertical" style={{ width: '100%' }}>
                              <Text>
                                <strong>Authors:</strong> {formatAuthors(paper.authors)}
                              </Text>
                              {paper.lab.pi && (
                                <Text>
                                  <strong>Lab PI:</strong> {paper.lab.pi}
                                </Text>
                              )}
                              {paper.abstract && (
                                <Paragraph
                                  ellipsis={{ 
                                    rows: 3, 
                                    expandable: true, 
                                    symbol: 'more',
                                    onExpand: () => console.log('expanded')
                                  }}
                                  style={{ marginTop: 8 }}
                                >
                                  {paper.abstract}
                                </Paragraph>
                              )}
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                </Card>
              ) : (
                <Card 
                  title="Latest ArXiv cs.RO Papers"
                  loading={arxivLoading}
                  extra={
                    <Button 
                      onClick={loadArxivPapers}
                      icon={<ReloadOutlined />}
                      size="small"
                    >
                      Refresh
                    </Button>
                  }
                >
                  <List
                    itemLayout="vertical"
                    size="large"
                    pagination={{
                      onChange: (page) => setCurrentPage(page),
                      pageSize: 10,
                      showSizeChanger: true,
                      showQuickJumper: true,
                      showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} papers`,
                    }}
                    dataSource={arxivPapers}
                    renderItem={(paper: any) => (
                      <List.Item
                        key={paper.id || paper.title}
                        actions={[
                          <Space key="actions">
                            {paper.pdf_url && (
                              <Button
                                type="link"
                                icon={<FileTextOutlined />}
                                href={paper.pdf_url}
                                target="_blank"
                                size="small"
                              >
                                PDF
                              </Button>
                            )}
                            {paper.arxiv_url && (
                              <Button
                                type="link"
                                href={paper.arxiv_url}
                                target="_blank"
                                size="small"
                              >
                                ArXiv
                              </Button>
                            )}
                          </Space>
                        ]}
                        extra={
                          <Space direction="vertical" align="end">
                            <Tag color="blue">ArXiv cs.RO</Tag>
                            <Tag color="green">New Submission</Tag>
                            {paper.publication_date && (
                              <Text type="secondary">
                                <CalendarOutlined /> {new Date(paper.publication_date).toLocaleDateString()}
                              </Text>
                            )}
                          </Space>
                        }
                      >
                        <List.Item.Meta
                          title={
                            <Space>
                              <Text strong style={{ fontSize: '16px' }}>
                                {paper.title}
                              </Text>
                              <Tag color="orange">preprint</Tag>
                            </Space>
                          }
                          description={
                            <Space direction="vertical" style={{ width: '100%' }}>
                              <Text>
                                <strong>Authors:</strong> {formatAuthors(paper.authors)}
                              </Text>
                              <Text>
                                <strong>ArXiv ID:</strong> {paper.arxiv_id}
                              </Text>
                              {paper.abstract && (
                                <Paragraph
                                  ellipsis={{ 
                                    rows: 3, 
                                    expandable: true, 
                                    symbol: 'more',
                                    onExpand: () => console.log('expanded')
                                  }}
                                  style={{ marginTop: 8 }}
                                >
                                  {paper.abstract}
                                </Paragraph>
                              )}
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                </Card>
              )}
            </Col>
          </Row>
        </Content>
      </Layout>
      
      <Footer style={{ textAlign: 'center' }}>
        Robotics SOTA ©2025 - Interactive Research Trends Mapping
      </Footer>

      <Modal
        title="Scrape Latest Papers"
        open={scrapeModalVisible}
        onOk={handleScrapePapers}
        onCancel={() => setScrapeModalVisible(false)}
        confirmLoading={scrapingInProgress}
        width={600}
      >
        <div style={{ marginBottom: 16 }}>
          <h4>Select Labs to Scrape:</h4>
          <div style={{ maxHeight: 200, overflowY: 'auto', border: '1px solid #d9d9d9', padding: 8 }}>
            <Checkbox
              indeterminate={selectedLabsForScraping.length > 0 && selectedLabsForScraping.length < labs.length}
              checked={selectedLabsForScraping.length === labs.length}
              onChange={(e) => {
                if (e.target.checked) {
                  setSelectedLabsForScraping(labs.map(lab => lab.id));
                } else {
                  setSelectedLabsForScraping([]);
                }
              }}
            >
              Select All ({labs.length} labs)
            </Checkbox>
            <Divider style={{ margin: '8px 0' }} />
            {labs.map(lab => (
              <div key={lab.id} style={{ marginBottom: 4 }}>
                <Checkbox
                  checked={selectedLabsForScraping.includes(lab.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedLabsForScraping([...selectedLabsForScraping, lab.id]);
                    } else {
                      setSelectedLabsForScraping(selectedLabsForScraping.filter(id => id !== lab.id));
                    }
                  }}
                >
                  {lab.name} {lab.paper_count ? `(${lab.paper_count} papers)` : '(no papers)'}
                </Checkbox>
              </div>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <h4>Select Sources:</h4>
          <Checkbox.Group
            value={scrapingSources}
            onChange={setScrapingSources}
          >
            <Space direction="vertical">
              <Checkbox value="arxiv">ArXiv (Academic Papers)</Checkbox>
              <Checkbox value="scholar">Google Scholar (Citations)</Checkbox>
              <Checkbox value="website">Lab Website (Recent Publications)</Checkbox>
            </Space>
          </Checkbox.Group>
        </div>

        <div style={{ marginBottom: 16 }}>
          <h4>Maximum Papers per Lab:</h4>
          <Select
            value={maxPapersToScrape}
            onChange={setMaxPapersToScrape}
            style={{ width: 200 }}
          >
            <Select.Option value={1}>1 paper</Select.Option>
            <Select.Option value={3}>3 papers</Select.Option>
            <Select.Option value={5}>5 papers</Select.Option>
            <Select.Option value={10}>10 papers</Select.Option>
            <Select.Option value={20}>20 papers</Select.Option>
          </Select>
        </div>

        <Alert
          message="Paper Scraping Info"
          description={`This will scrape up to ${maxPapersToScrape} recent papers per lab from the selected sources. The process may take a few minutes.`}
          type="info"
          showIcon
        />
      </Modal>

      <Modal
        title="Find Other Lab Papers (Institutional Search)"
        open={showInstitutionalScrapeModal}
        onOk={handleInstitutionalScraping}
        onCancel={() => setShowInstitutionalScrapeModal(false)}
        confirmLoading={scrapingInProgress}
        width={600}
      >
        <div style={{ marginBottom: 16 }}>
          <Alert
            message="Institutional Paper Discovery"
            description="This feature searches for robotics papers from researchers at specific institutions using keywords, titles, and author patterns. Papers found will be displayed as 'Other Labs' with extracted author information."
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          
          <h4>Search Parameters:</h4>
          <ul style={{ paddingLeft: 20, marginBottom: 16 }}>
            <li>Institution-based searches (universities, research centers)</li>
            <li>Robotics keywords filtering (manipulation, perception, navigation, etc.)</li>
            <li>Recent publications (last 2-3 years)</li>
            <li>Author name and affiliation extraction</li>
          </ul>
          
          <div style={{ marginBottom: 16 }}>
            <h4>Max Papers to Find:</h4>
            <Select
              value={maxPapersToScrape}
              onChange={setMaxPapersToScrape}
              style={{ width: '100%' }}
            >
              <Option value={1}>1 paper</Option>
              <Option value={3}>3 papers</Option>
              <Option value={5}>5 papers</Option>
              <Option value={10}>10 papers</Option>
              <Option value={20}>20 papers</Option>
            </Select>
          </div>
          
          <Alert
            message="Note"
            description="This search will look for papers from researchers at major universities and research institutions not currently in your lab database."
            type="warning"
            showIcon
          />
        </div>
      </Modal>

      <LabFormModal
        visible={labFormVisible}
        onCancel={() => setLabFormVisible(false)}
        onSuccess={handleLabFormSuccess}
        lab={currentLab}
        mode={formMode}
      />

      <PaperFormModal
        visible={paperModalVisible}
        onCancel={handlePaperModalCancel}
        onSuccess={handlePaperModalSuccess}
        paper={editingPaper}
        mode={paperModalMode}
        labId={selectedLabId || 0}
      />
    </Layout>
  );
};

export default App;