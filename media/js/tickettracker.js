TicketTracker = (function () {
	var r = {
		testing: function () {
		},
		Forms: {
			focusListElement: function (ev) {
				$(this).closest('li').addClass('focused');
			},
			blurSelectedListElement: function (ev) {
				$(this).closest('li').removeClass('focused');
			},
			initialize: function () {
				$('.tt-form ol li input, .tt-form ol li select, .tt-form ol li textarea').unbind('focus').bind('focus', this.focusListElement).unbind('blur').bind('blur', this.blurSelectedListElement);
				$('.tt-date-field input').datepicker();
			}
		},
		BurndownChart: {
			queryAndDraw: function () {
				var url = '/burndown-chart/data/', classes = '';

				if ($('#tt-burndownchart-lines').hasClass('tt-sprint-id')) {
					classes = $('#tt-burndownchart-lines').attr('class');
					url = url + 'sprint/' + classes.replace(/tt-sprint-id /, '').replace(/tt-sprint-/, '') + '/';
				}

				$.get(url, function (chart_data) {
					var i = 0, j = chart_data.length, data = new google.visualization.DataTable();
					data.addColumn('string', 'Date');
					data.addColumn('number', 'Score');
					data.addColumn('number', 'Task Score');
					data.addColumn('number', 'Fire Score');
					for (; i < j; i += 1) {
						data.addRow(chart_data[i]);
					}
					new google.visualization.LineChart(document.getElementById('tt-burndownchart-lines')).draw(data, {
						width: $('#tt-burndownchart-lines').outerWidth(), height: $(window).height() - $('#tt-head').outerHeight() - $('h2').outerHeight(),
						vAxis: {maxValue: chart_data[0][1], minValue: 0},
						fontName: 'Open Sans Condensed',
						chartArea: {
							top: 50, left: 55,
							width: $('#tt-burndownchart-lines').outerWidth() - 200, height: $(window).height() - $('#tt-head').outerHeight() - $('h2').outerHeight() - 150
						},
						colors: ['#5f8e00', '#0D9FD9', '#F5380C']
					});
				}, 'json');
			},
			initialize: function () {
				// Google libs obviously attach themselves to window
				if (window.google) {
					window.google.load('visualization', '1', {packages: ['corechart']});
					window.google.setOnLoadCallback(this.queryAndDraw);
				}
			}
		},
		Stories: {
			idSequence: ['story_id', 'sprint_id'],
			backlogActionList: {
				'Add to Sprint': '/planning/sprint/{{sprint_id}}/stories/add/{{story_id}}/',
				'Duplicate Story': '/backlog/story/{{story_id}}/copy/'
			},
			sprintActionList: {
				'Remove from Sprint': '/planning/sprint/{{sprint_id}}/stories/remove/{{story_id}}/',
				'Set owner(s)': '/planning/sprint/{{sprint_id}}/stories/owner/{{story_id}}/',
				'Duplicate Story': '/backlog/story/{{story_id}}/copy/'
			},
			toggleStoryElements: function (ev, that) {
				var elm = $(that || this);
				if (elm.hasClass('tt-show')) {
					elm.closest('li').find('ol, p, span').css('display', 'none');
					elm.removeClass('tt-show');
				} else {
					elm.closest('li').find('ol, p, span').css('display', 'block');
					elm.addClass('tt-show');
				}
				ev.preventDefault();
			},
			initBoardDND: function () {
				$('#tt-board #tt-board-columns li ul.tt-side-list .tt-board-story-actions').remove(); // Remove classical way of moving tickets
				$('#tt-board #tt-board-columns li ul.tt-side-list').sortable({
					handle: 'h6',
					containment: '#tt-board #tt-board-columns',
					connectWith: '#tt-board #tt-board-columns li ul.tt-side-list',
					helper: 'clone',
					revert: 'invalid',
					receive: function (ev, ui) {
						var senderTag = ui.sender.attr('id').replace('tt-backlog-list-', ''),
							receiverTag = ui.item.closest('.tt-side-list').attr('id').replace('tt-backlog-list-', ''),
							id = ui.item.find('h6 a').attr('id').replace('tt-story-id-', ''),
							validMove = true;
						if (senderTag === receiverTag) {
							$(ui.sender).sortable('cancel');
							validMove = false;
						}
						if (ui.item.find('h6 a').hasClass('tt-fire') && receiverTag === 'DONE') {
							// This is a fire story
							$(ui.sender).sortable('cancel');
							validMove = false;
						} else if (!ui.item.find('h6 a').hasClass('tt-fire') && receiverTag === 'FIRE') {
							// This is not a fire story
							$(ui.sender).sortable('cancel');
							validMove = false;
						}
						if (validMove && !!id) {
							$.get('/board/story/move/' + id + '/' + receiverTag + '/', function () {
								// Should I do anything here?
							});
						}
					}
				});
			},
			createActionsList: function (story, actionList, ids) {
				var key = '', url = '', li = null, counter = 0;
				story.find('ol').empty();
				for (key in actionList) {
					url = actionList[key];
					li = $('<li>').append($('<a>', {
						text: key,
						href: function () {
							var i = 0, j = ids.length, toReturn = actionList[key];
							for (; i < j; i += 1) {
								toReturn = toReturn.replace('{{' + r.Stories.idSequence[i] + '}}', ids[i]);
							}
							return toReturn;
						}()
					}));
					if (counter++ === 0) {
						li.find('a').attr('class', 'tt-ids').attr('id', 'tt-ids-' + ids[0] + '-' + ids[1]);
					}
					story.find('ol').append(li);
				}
			},
			initPlanningDND: function () {
				$('#tt-planning .tt-sprint-planning-stories .tt-ids').css('display', 'none');
				$('#tt-planning .tt-sprint-planning-stories').sortable({
					handle: 'h6',
					containment: '#tt-planning',
					connectWith: '.tt-sprint-planning-stories',
					helper: 'clone',
					revert: 'invalid',
					receive: function (ev, ui) {
						var ids = [];
						if (ui.sender.attr('id') === 'tt-backlog-available') {
							ids = ui.item.find('.tt-ids').attr('id').replace(/tt-ids-/, '').split('-');
							$.get(ui.item.find('.tt-ids').attr('href'), function () {
								r.Stories.createActionsList(ui.item, r.Stories.sprintActionList, ids);
								$('h2.tt-planning span').text(parseInt($('h2.tt-planning span').text()) - parseInt(ui.item.find('span').text().replace(/[^\d.]/g, '')));
							});
						} else if (ui.sender.attr('id') === 'tt-sprint-set') {
							ids = ui.item.find('.tt-ids').attr('id').replace(/tt-ids-/, '').split('-');
							$.get(ui.item.find('.tt-ids').attr('href'), function () {
								r.Stories.createActionsList(ui.item, r.Stories.backlogActionList, ids);
								$('h2.tt-planning span').text(parseInt($('h2.tt-planning span').text()) + parseInt(ui.item.find('span').text().replace(/[^\d.]/g, '')));
							});
						}
					}
				});
			},
			initialize: function () {
				if (navigator.userAgent.match(/iPad/i) == null) {
					$('.tt-side-list:not(.tt-non-collapsible, ol li)').find('ol, p, span').css('display', 'none');
					$('.tt-side-list:not(.tt-non-collapsible, ol li)').undelegate().delegate('h6 a', 'click', this.toggleStoryElements);
					this.initPlanningDND();
					this.initBoardDND();
				}
				// Disable text selection for story titles
				//$('h6 a').disableTextSelect();
			}
		}
	},
	u = {
		application: {
			version: '0.9',
			applicationName: 'tickettracker',
			activejQuery: '1.7.1',
			documentation: 'tt.panco.si/documentation'
		},
		initialize: function () {
			r.Forms.initialize();
			r.Stories.initialize();
			r.BurndownChart.initialize();
			// Make the whole object available
			return this;
		}
	};
	return u.initialize();
})();